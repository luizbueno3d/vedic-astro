"""FastAPI application for Vedic astrology calculations."""

import os
import sys
import hmac
import hashlib
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent.parent.parent / '.env')
except ImportError:
    pass

from fastapi import FastAPI, HTTPException, Request, Query, UploadFile, File, Form

from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, Response
from starlette.middleware.sessions import SessionMiddleware
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from datetime import date
import json

from engine.ephemeris import calculate_chart, deg_to_dms, get_rashi_lord, RASHIS
from engine.charts import get_varga_signs, VARGA_FUNCTIONS, VARGA_META
from engine.kp import calculate_kp_bhava_chalit, kp_to_dict
from engine.jaimini import calculate_chara_karakas, calculate_chara_dasha, calculate_jaimini_raja_yoga, calculate_karakamsa, get_jaimini_interpretation, get_jaimini_sign_aspects, interpret_chara_dasha, interpret_karakamsa
from engine.dasha import (
    calculate_mahadasha, calculate_antardasha, calculate_pratyantardasha,
    get_current_dasha_periods, dasha_to_dict, get_starting_dasha
)
from engine.transits import build_transit_reading, calculate_transits, find_sign_changes, transit_to_dict
from engine.aspects import find_conjunctions, find_aspects, conjunction_to_dict, aspect_to_dict
from engine.yogas import detect_all_yogas, yoga_to_dict, calculate_house_rulerships
from engine.bhavat_bhavam import get_all_bhavat_bhavam, get_planet_bhavat_bhavam, get_planet_house_from_house_analysis
from engine.ashtakavarga import calculate_sarva_ashtakavarga, interpret_sav_score
from engine.shadbala import calculate_shadbala
from engine.doshas import detect_all_doshas, dosha_to_dict
from engine.guna_milan import calculate_guna_milan
from engine.synastry import calculate_synastry
from engine.reading import generate_reading
from engine.synthesis import synthesize
from engine.llm_reading import generate_llm_reading
from engine.ai_provider import (
    load_config, save_config, get_active_provider, update_provider,
    test_provider, generate_reading as ai_generate_reply, PROVIDER_MODELS,
    DEFAULT_PROVIDERS, AIProvider
)
from engine.geocoding import geocode, search_places
from engine.firebase_auth import get_firebase_web_config, firebase_client_enabled, verify_firebase_id_token
from engine.timezone_utils import get_tz_offset_for_date
from engine.transcription import transcribe_audio
from data.database import (
    list_profiles, get_profile, add_profile, update_profile,
    delete_profile, seed_default_profiles, assign_owner_uid
)

app = FastAPI(title="Vedic Astro", version="1.0.0")

APP_SESSION_SECRET = os.getenv("APP_SESSION_SECRET", "vedic-astro-session-secret-change-me")
DEFAULT_OWNER_EMAIL = os.getenv("DEFAULT_OWNER_EMAIL", "luizbueno3d@gmail.com")
AUTH_COOKIE_NAME = "vedic_astro_auth"
PUBLIC_PATHS = {
    "/login",
    "/api",
    "/auth/firebase-login",
}

app.add_middleware(
    SessionMiddleware,
    secret_key=APP_SESSION_SECRET,
    session_cookie="vedic_astro_session",
    same_site="lax",
    https_only=True,
)

# Templates
import os as _os
_base_dir = _os.path.dirname(_os.path.dirname(_os.path.dirname(__file__)))
templates_dir = _os.path.join(_base_dir, 'templates')

# Ensure templates dir exists
_os.makedirs(templates_dir, exist_ok=True)

templates = Jinja2Templates(directory=templates_dir)


def _session_data(request: Request) -> dict:
    session = request.scope.get("session")
    return session if isinstance(session, dict) else {}


def _auth_cookie_value() -> str:
    return hmac.new(
        APP_SESSION_SECRET.encode("utf-8"),
        b"vedic-astro-authenticated",
        hashlib.sha256,
    ).hexdigest()


def _is_authenticated(request: Request) -> bool:
    cookie = request.cookies.get(AUTH_COOKIE_NAME)
    if not cookie:
        return False
    return hmac.compare_digest(cookie, _auth_cookie_value())


def _current_owner_email(request: Request) -> str:
    owner_email = _session_data(request).get("user_email")
    if not owner_email:
        raise HTTPException(401, "Authentication required")
    return owner_email


def _current_owner_uid(request: Request) -> str | None:
    return _session_data(request).get("user_uid")


def _login_redirect() -> RedirectResponse:
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie(AUTH_COOKIE_NAME, path="/")
    response.delete_cookie("vedic_astro_session", path="/")
    return response


def _is_html_request(request: Request) -> bool:
    accept = request.headers.get("accept", "")
    return "text/html" in accept


def _ai_template_state(owner_email: str) -> dict:
    provider = get_active_provider(owner_email)
    return {
        "active_ai_enabled": bool(provider),
        "active_ai_provider_label": provider.label if provider else "",
    }


def _build_ai_chat_prompt(page: str, chart, question: str, extra: str = "") -> tuple[str, str]:
    moon = chart.planets['Moon']
    system = (
        "You are a concise, insightful Vedic astrology guide inside a private astrology app. "
        "Answer the user's question using the supplied chart context and the current page context. "
        "Be specific, practical, and pedagogical. If a page-specific layer is secondary, say so. "
        "Do not invent facts not present in the supplied data. Keep replies to 2-6 short paragraphs."
    )
    user = f"""Page: {page}
Profile: {chart.name}
Ascendant: {chart.ascendant.rashi}
Moon: {moon.rashi} in {moon.nakshatra} pada {moon.pada}

{extra.strip()}

Question: {question}"""
    return system, user


@app.middleware("http")
async def auth_gate(request: Request, call_next):
    path = request.url.path

    if request.method == "OPTIONS":
        return await call_next(request)

    if path in PUBLIC_PATHS or path.startswith("/login"):
        return await call_next(request)

    if _is_authenticated(request):
        return await call_next(request)

    if _is_html_request(request):
        return _login_redirect()

    return JSONResponse({"error": "Authentication required"}, status_code=401)


# ===== Pydantic Models =====

class BirthData(BaseModel):
    name: str = ''
    year: int
    month: int
    day: int
    hour: int
    minute: int
    latitude: float
    longitude: float
    place: str = ''
    tz_offset: float = -3.0


class ProfileCreate(BaseModel):
    name: str
    birth_date: str  # YYYY-MM-DD
    birth_time: str  # HH:MM
    birth_place: str
    latitude: float
    longitude: float
    tz_offset: float = -3.0
    notes: str = ''


# ===== API Routes =====

@app.on_event("startup")
async def startup():
    seed_default_profiles()


@app.get("/api")
async def api_root():
    return {"app": "Vedic Astro", "version": "1.0.0", "endpoints": ["/profiles", "/chart", "/chart/{profile_id}", "/dasha/{profile_id}", "/transits/{profile_id}", "/vargas/{profile_id}", "/compatibility"]}

@app.get("/")
async def root():
    return RedirectResponse(url="/dashboard")


@app.get("/login", response_class=HTMLResponse)
async def page_login(request: Request, error: str = Query(None)):
    if _is_authenticated(request):
        return RedirectResponse(url="/dashboard", status_code=303)
    response = templates.TemplateResponse("login.html", {
        "request": request,
        "page": "login",
        "profiles": [],
        "profile_id": None,
        "is_authenticated": False,
        "error": error,
        "firebase_enabled": firebase_client_enabled(),
        "firebase_config": json.dumps(get_firebase_web_config()),
    })
    response.delete_cookie(AUTH_COOKIE_NAME, path="/")
    response.delete_cookie("vedic_astro_session", path="/")
    return response


@app.post("/login")
async def api_login(request: Request, password_form: str = Form(None)):
    if _is_html_request(request):
        return RedirectResponse(url="/login?error=Use%20Firebase%20sign-in", status_code=303)
    return JSONResponse({"error": "Use Firebase sign-in"}, status_code=401)


@app.post("/logout")
async def api_logout(request: Request):
    _session_data(request).clear()
    response = JSONResponse({"success": True})
    response.delete_cookie(AUTH_COOKIE_NAME, path="/")
    response.delete_cookie("vedic_astro_session", path="/")
    return response


@app.post("/auth/firebase-login")
async def api_firebase_login(request: Request):
    data = await request.json()
    token = data.get('idToken', '')
    claims = verify_firebase_id_token(token)
    if not claims:
        return JSONResponse({'error': 'Firebase token verification failed'}, status_code=401)

    email = claims.get('email')
    uid = claims.get('uid')
    if not email:
        return JSONResponse({'error': 'Firebase account has no email'}, status_code=400)

    session = _session_data(request)
    session['user_email'] = email
    session['user_uid'] = uid
    if uid:
        assign_owner_uid(email, uid)
    response = JSONResponse({'success': True, 'email': email})
    response.set_cookie(
        AUTH_COOKIE_NAME,
        _auth_cookie_value(),
        httponly=True,
        secure=True,
        samesite='lax',
        path='/',
        max_age=60 * 60 * 24 * 14,
    )
    return response


# --- Profiles ---

@app.get("/profiles")
async def api_list_profiles(request: Request):
    return list_profiles(_current_owner_email(request))


@app.post("/profiles")
async def api_create_profile(request: Request, data: ProfileCreate):
    pid = add_profile(
        data.name, data.birth_date, data.birth_time,
        data.birth_place, data.latitude, data.longitude,
        data.tz_offset, data.notes,
        owner_email=_current_owner_email(request),
        owner_uid=_current_owner_uid(request),
    )
    return {"id": pid, "message": f"Profile '{data.name}' created"}


@app.get("/profiles/{profile_id}")
async def api_get_profile(request: Request, profile_id: int):
    p = get_profile(profile_id, _current_owner_email(request))
    if not p:
        raise HTTPException(404, "Profile not found")
    return p


@app.delete("/profiles/{profile_id}")
async def api_delete_profile(request: Request, profile_id: int):
    if delete_profile(profile_id, _current_owner_email(request)):
        return {"message": "Deleted"}
    raise HTTPException(404, "Profile not found")


# --- Chart ---

def _chart_from_birth(data: BirthData):
    return calculate_chart(
        data.year, data.month, data.day, data.hour, data.minute,
        data.latitude, data.longitude, data.name, data.place, data.tz_offset
    )


def _chart_from_profile(profile_id: int, owner_email: str):
    p = get_profile(profile_id, owner_email)
    if not p:
        raise HTTPException(404, "Profile not found")
    bdate = p['birth_date'].split('-')
    btime = p['birth_time'].split(':')
    return calculate_chart(
        int(bdate[0]), int(bdate[1]), int(bdate[2]),
        int(btime[0]), int(btime[1]),
        p['latitude'], p['longitude'], p['name'],
        p['birth_place'], p.get('tz_offset', -3.0)
    )


def _serialize_chart(chart) -> dict:
    planets = {}
    for name, p in chart.planets.items():
        planets[name] = {
            'name': p.name,
            'longitude': round(p.longitude, 4),
            'rashi': p.rashi,
            'rashi_index': p.rashi_index,
            'rashi_lord': get_rashi_lord(p.rashi_index),
            'nakshatra': p.nakshatra,
            'pada': p.pada,
            'house': p.house,
            'retrograde': p.retrograde,
            'degree_in_sign': round(p.degree_in_sign, 4),
            'degree_formatted': deg_to_dms(p.degree_in_sign),
        }

    asc = chart.ascendant
    return {
        'name': chart.name,
        'birth_date': chart.birth_date,
        'birth_time': chart.birth_time,
        'birth_place': chart.birth_place,
        'ayanamsa': round(chart.ayanamsa, 6),
        'ascendant': {
            'rashi': asc.rashi,
            'nakshatra': asc.nakshatra,
            'pada': asc.pada,
            'longitude': round(asc.longitude, 4),
            'degree_formatted': deg_to_dms(asc.longitude),
        },
        'planets': planets,
    }


HOUSE_TOPICS = {
    1: 'identity, body, and self-direction',
    2: 'money, speech, and family resources',
    3: 'skills, courage, writing, and initiative',
    4: 'home, roots, private life, and emotional security',
    5: 'creativity, romance, children, and intelligence',
    6: 'work, service, health, and conflict',
    7: 'partnerships, clients, and public dealings',
    8: 'transformation, crisis, secrecy, and depth',
    9: 'belief, teachers, travel, and higher meaning',
    10: 'career, reputation, duty, and visibility',
    11: 'gains, networks, allies, and long-term goals',
    12: 'retreat, loss, sleep, foreignness, and liberation',
}


def _format_duration_label(years: float) -> str:
    total_months = max(1, int(round(years * 12)))
    year_part, month_part = divmod(total_months, 12)
    bits = []
    if year_part:
        bits.append(f"{year_part}y")
    if month_part:
        bits.append(f"{month_part}m")
    return ' '.join(bits) if bits else '<1m'


def _period_blurb(lord: str, chart, kp, rulerships: dict[str, list[int]], level_label: str) -> str:
    natal = chart.planets.get(lord)
    if not natal:
        return f'{level_label} of {lord} is active now.'
    kp_placement = kp.planets.get(lord) if kp else None
    kp_house = kp_placement.kp_house if kp_placement else natal.house
    natal_topic = HOUSE_TOPICS.get(natal.house, 'its natal house topics')
    kp_topic = HOUSE_TOPICS.get(kp_house, 'the life area where results land')
    ruled = rulerships.get(lord, [])
    ruled_text = f" It also rules H{', H'.join(str(h) for h in ruled)}." if ruled else ''
    return f'{lord} starts from {natal.rashi} H{natal.house} ({natal_topic}) and tends to deliver results through BCC H{kp_house} ({kp_topic}).{ruled_text}'


def _serialize_mahadasha_timeline(mahadashas: list) -> list[dict]:
    today_iso = date.today().isoformat()
    timeline = []
    for idx, md in enumerate(mahadashas):
        md_dict = dasha_to_dict(md)
        md_dict['index'] = idx
        md_dict['duration_label'] = _format_duration_label(md.years)
        md_dict['state'] = 'past' if md_dict['end'] < today_iso else 'future'
        if md_dict['is_current']:
            md_dict['state'] = 'current'

        antardashas = []
        for ad_idx, ad in enumerate(calculate_antardasha(md)):
            ad_dict = dasha_to_dict(ad)
            ad_dict['index'] = ad_idx
            ad_dict['duration_label'] = _format_duration_label(ad.years)
            ad_dict['state'] = 'past' if ad_dict['end'] < today_iso else 'future'
            if ad_dict['is_current']:
                ad_dict['state'] = 'current'

            pratyantardashas = []
            for pd_idx, pd in enumerate(calculate_pratyantardasha(ad, md.years)):
                pd_dict = dasha_to_dict(pd)
                pd_dict['index'] = pd_idx
                pd_dict['duration_label'] = _format_duration_label(pd.years)
                pd_dict['state'] = 'past' if pd_dict['end'] < today_iso else 'future'
                if pd_dict['is_current']:
                    pd_dict['state'] = 'current'
                pratyantardashas.append(pd_dict)

            ad_dict['pratyantardashas'] = pratyantardashas
            antardashas.append(ad_dict)

        md_dict['antardashas'] = antardashas
        timeline.append(md_dict)
    return timeline


def _build_current_dasha_reading(chart, current: dict, kp) -> list[dict]:
    rulerships = calculate_house_rulerships(chart.ascendant.rashi_index)
    reading = []

    for level in ['mahadasha', 'antardasha', 'pratyantardasha']:
        period = current.get(level)
        if not period:
            continue

        natal = chart.planets.get(period.lord)
        kp_placement = kp.planets.get(period.lord) if kp else None
        if not natal:
            continue

        ruled_houses = rulerships.get(period.lord, [])
        natal_topic = HOUSE_TOPICS.get(natal.house, 'the life area shown by that house')
        kp_house = kp_placement.kp_house if kp_placement else natal.house
        kp_topic = HOUSE_TOPICS.get(kp_house, 'the life area shown by that house')
        ruled_text = ', '.join(f'H{house}' for house in ruled_houses) if ruled_houses else 'no major houses'
        label = {
            'mahadasha': 'Mahadasha',
            'antardasha': 'Antardasha',
            'pratyantardasha': 'Pratyantardasha',
        }[level]

        summary = (
            f'{label} of {period.lord} activates the natal {period.lord} placed in {natal.rashi} in H{natal.house}. '
            f'In D1 this planet starts from {natal_topic}, while in BCC/KP its manifestation shifts to H{kp_house}, '
            f'bringing concrete results into {kp_topic}.'
        )
        practical = (
            f'Read {period.lord} through both layers at once: natal promise from H{natal.house}, lived manifestation from BCC H{kp_house}, '
            f'and house rulership through {ruled_text}. During this period, topics of {natal_topic} tend to deliver outcomes through {kp_topic}.'
        )

        reading.append({
            'level': label,
            'lord': period.lord,
            'start': period.start.isoformat(),
            'end': period.end.isoformat(),
            'natal_sign': natal.rashi,
            'natal_house': natal.house,
            'kp_house': kp_house,
            'houses_ruled': ruled_houses,
            'summary': summary,
            'practical': practical,
        })

    return reading


@app.post("/chart")
async def api_chart_from_birth(data: BirthData):
    chart = _chart_from_birth(data)
    return _serialize_chart(chart)


@app.get("/chart/{profile_id}")
async def api_chart_from_profile(request: Request, profile_id: int):
    chart = _chart_from_profile(profile_id, _current_owner_email(request))
    return _serialize_chart(chart)


# --- Divisional Charts ---

@app.get("/vargas/{profile_id}")
async def api_vargas(request: Request, profile_id: int, varga: str = None):
    chart = _chart_from_profile(profile_id, _current_owner_email(request))
    all_vargas = get_varga_signs(chart)

    if varga:
        if varga not in all_vargas:
            raise HTTPException(400, f"Unknown varga: {varga}. Options: {list(all_vargas.keys())}")
        return {varga: all_vargas[varga]}

    return all_vargas


# --- KP Bhava Chalit ---

@app.get("/kp/{profile_id}")
async def api_kp(request: Request, profile_id: int):
    chart = _chart_from_profile(profile_id, _current_owner_email(request))
    kp = calculate_kp_bhava_chalit(chart)
    return kp_to_dict(kp)


# --- Dasha ---

@app.get("/dasha/{profile_id}")
async def api_dasha(request: Request, profile_id: int, level: str = 'all'):
    chart = _chart_from_profile(profile_id, _current_owner_email(request))
    moon_lon = chart.planets['Moon'].longitude
    birth_date = date.fromisoformat(chart.birth_date)
    kp = calculate_kp_bhava_chalit(chart)

    mahadashas = calculate_mahadasha(birth_date, moon_lon)

    if level == 'mahadasha':
        return {'mahadashas': _serialize_mahadasha_timeline(mahadashas)}

    # Find current MD and get its antardashas
    current = get_current_dasha_periods(mahadashas)

    result = {
        'starting_dasha': get_starting_dasha(moon_lon)[0],
        'mahadashas': _serialize_mahadasha_timeline(mahadashas),
        'current': {},
    }

    if current['mahadasha']:
        result['current']['mahadasha'] = dasha_to_dict(current['mahadasha'])
        antardashas = calculate_antardasha(current['mahadasha'])
        result['current']['antardashas'] = [dasha_to_dict(ad) for ad in antardashas]

        if current['antardasha']:
            result['current']['antardasha'] = dasha_to_dict(current['antardasha'])
            pratyantardashas = calculate_pratyantardasha(
                current['antardasha'], current['mahadasha'].years
            )
            result['current']['pratyantardashas'] = [dasha_to_dict(pd) for pd in pratyantardashas]

            if current['pratyantardasha']:
                result['current']['pratyantardasha'] = dasha_to_dict(current['pratyantardasha'])

    result['current_reading'] = _build_current_dasha_reading(chart, current, kp)

    return result


# --- Transits ---

@app.get("/transits/{profile_id}")
async def api_transits(request: Request, profile_id: int, date_str: str = None):
    chart = _chart_from_profile(profile_id, _current_owner_email(request))
    target = date.fromisoformat(date_str) if date_str else None
    transits = calculate_transits(chart, target)
    return {name: transit_to_dict(tp) for name, tp in transits.items()}


@app.get("/sign-changes/{planet}")
async def api_sign_changes(planet: str, year: int = None):
    if year is None:
        year = date.today().year
    changes = find_sign_changes(year, planet)
    return {'planet': planet, 'year': year, 'changes': changes}


# --- Compatibility ---

@app.get("/compatibility/{profile_id_1}/{profile_id_2}")
async def api_compatibility(request: Request, profile_id_1: int, profile_id_2: int):
    owner_email = _current_owner_email(request)
    chart1 = _chart_from_profile(profile_id_1, owner_email)
    chart2 = _chart_from_profile(profile_id_2, owner_email)

    moon1 = chart1.planets['Moon']
    moon2 = chart2.planets['Moon']

    moon_dist = (moon2.rashi_index - moon1.rashi_index) % 12

    synastry = calculate_synastry(chart1, chart2)

    guna_milan = calculate_guna_milan(moon1, moon2)

    return {
        'person_1': chart1.name,
        'person_2': chart2.name,
        'moon_1': {'rashi': moon1.rashi, 'nakshatra': moon1.nakshatra},
        'moon_2': {'rashi': moon2.rashi, 'nakshatra': moon2.nakshatra},
        'moon_distance': moon_dist,
        'ascendant_1': chart1.ascendant.rashi,
        'ascendant_2': chart2.ascendant.rashi,
        'interpretation': _moon_distance_interpretation(moon_dist),
        'guna_milan': guna_milan,
        'synastry': synastry,
    }


def _moon_distance_interpretation(dist: int) -> str:
    interpretations = {
        0: 'Same sign — deep understanding but may lack growth',
        1: '2/12 — challenging, different life rhythms',
        2: '3/11 — growth-oriented, mutual support',
        3: '4/10 — complementary but different approaches',
        4: '5/9 — creative and fortunate connection',
        5: '6/8 — transformative but intense',
        6: '7/7 — natural harmony, strong attraction',
        7: '8/6 — karmic, transformative',
        8: '9/5 — fortunate, philosophical bond',
        9: '10/4 — complementary, different directions',
        10: '11/3 — growth through shared goals',
        11: '12/1 — spiritually connected but different',
    }
    return interpretations.get(dist, 'Unknown')


# --- Aspects & Yogas ---

@app.get("/aspects/{profile_id}")
async def api_aspects(request: Request, profile_id: int):
    chart = _chart_from_profile(profile_id, _current_owner_email(request))
    conjs = find_conjunctions(chart.planets)
    asps = find_aspects(chart.planets)
    return {
        'conjunctions': [conjunction_to_dict(c) for c in conjs],
        'aspects': [aspect_to_dict(a) for a in asps],
    }


@app.get("/yogas/{profile_id}")
async def api_yogas(request: Request, profile_id: int):
    chart = _chart_from_profile(profile_id, _current_owner_email(request))
    rulerships = calculate_house_rulerships(chart.ascendant.rashi_index)
    yogas = detect_all_yogas(chart.planets, rulerships)
    return {
        'yogas': [yoga_to_dict(y) for y in yogas],
        'house_rulerships': {k: v for k, v in rulerships.items()},
    }


@app.get("/bhavat-bhavam/{profile_id}")
async def api_bhavat_bhavam(request: Request, profile_id: int):
    chart = _chart_from_profile(profile_id, _current_owner_email(request))
    bb = get_planet_bhavat_bhavam(chart.planets, {})
    planet_bb = get_planet_house_from_house_analysis(chart.planets)
    return {'bhavat_bhavam': bb, 'planet_bhavat_bhavam': planet_bb}


@app.get("/jaimini/{profile_id}")
async def api_jaimini(request: Request, profile_id: int):
    chart = _chart_from_profile(profile_id, _current_owner_email(request))
    karakas = calculate_chara_karakas(chart.planets)
    karakamsa = calculate_karakamsa(karakas, chart.planets)
    chara_dasha = calculate_chara_dasha(chart.planets, chart.ascendant.rashi_index, date.fromisoformat(chart.birth_date))
    return {
        'karakas': karakas,
        'interpretation': get_jaimini_interpretation(karakas),
        'raja_yogas': calculate_jaimini_raja_yoga(karakas),
        'karakamsa': karakamsa,
        'sign_aspects': get_jaimini_sign_aspects(chart.planets),
        'chara_dasha': chara_dasha,
    }


@app.get("/doshas/{profile_id}")
async def api_doshas(request: Request, profile_id: int):
    chart = _chart_from_profile(profile_id, _current_owner_email(request))
    doshas = detect_all_doshas(chart.planets)
    return {'doshas': [dosha_to_dict(d) for d in doshas]}


@app.get("/reading/{profile_id}")
async def api_reading(request: Request, profile_id: int):
    chart = _chart_from_profile(profile_id, _current_owner_email(request))
    rulerships = calculate_house_rulerships(chart.ascendant.rashi_index)
    moon_lon = chart.planets['Moon'].longitude
    birth_date = date.fromisoformat(chart.birth_date)
    mds = calculate_mahadasha(birth_date, moon_lon)
    current = get_current_dasha_periods(mds)
    dasha_data = {'current': {}}
    if current['mahadasha']: dasha_data['current']['mahadasha'] = dasha_to_dict(current['mahadasha'])
    if current['antardasha']: dasha_data['current']['antardasha'] = dasha_to_dict(current['antardasha'])
    if current['pratyantardasha']: dasha_data['current']['pratyantardasha'] = dasha_to_dict(current['pratyantardasha'])
    yogas = detect_all_yogas(chart.planets, rulerships)
    doshas = detect_all_doshas(chart.planets)
    sb = calculate_shadbala(chart.planets)
    sav = calculate_sarva_ashtakavarga(chart.planets, chart.ascendant.rashi_index)
    reading = generate_reading(chart, dasha_data, yogas, doshas, sb, sav, rulerships)
    return {'reading': reading}


@app.get("/llm-reading/{profile_id}")
async def api_llm_reading(request: Request, profile_id: int):
    """Generate an AI-powered reading using the configured provider."""
    owner_email = _current_owner_email(request)
    chart = _chart_from_profile(profile_id, owner_email)
    rulerships = calculate_house_rulerships(chart.ascendant.rashi_index)
    moon_lon = chart.planets['Moon'].longitude
    birth_date = date.fromisoformat(chart.birth_date)
    mds = calculate_mahadasha(birth_date, moon_lon)
    current = get_current_dasha_periods(mds)
    dasha_data = {'current': {}}
    if current['mahadasha']: dasha_data['current']['mahadasha'] = dasha_to_dict(current['mahadasha'])
    if current['antardasha']: dasha_data['current']['antardasha'] = dasha_to_dict(current['antardasha'])
    if current['pratyantardasha']: dasha_data['current']['pratyantardasha'] = dasha_to_dict(current['pratyantardasha'])
    yogas = detect_all_yogas(chart.planets, rulerships)
    doshas = detect_all_doshas(chart.planets)
    sb = calculate_shadbala(chart.planets)
    sav = calculate_sarva_ashtakavarga(chart.planets, chart.ascendant.rashi_index)
    conjs = find_conjunctions(chart.planets)
    asps = find_aspects(chart.planets)
    vargas = get_varga_signs(chart)
    transits = calculate_transits(chart)
    transits_data = {k: transit_to_dict(v) for k, v in transits.items()}

    provider = get_active_provider(owner_email)
    provider_name = provider.label if provider else 'none'

    llm_text = generate_llm_reading(
        chart, rulerships, yogas, doshas, sb, sav,
        dasha_data, transits_data, vargas,
        [conjunction_to_dict(c) for c in conjs], [aspect_to_dict(a) for a in asps],
        owner_email=owner_email,
    )

    return {'reading': llm_text, 'provider': provider_name}


@app.post("/ai-chat")
async def api_ai_chat(request: Request):
    owner_email = _current_owner_email(request)
    payload = await request.json()
    question = (payload.get('question') or '').strip()
    page = (payload.get('page') or 'dashboard').strip()
    profile_id = int(payload.get('profile_id') or payload.get('p1') or 0)
    p1 = payload.get('p1')
    p2 = payload.get('p2')

    provider = get_active_provider(owner_email)
    if not provider:
        return JSONResponse({
            'error': 'No AI model selected. Go to AI Interpretations, choose a provider/model, add your API key, and save it first.'
        }, status_code=400)

    if not question:
        return JSONResponse({'error': 'Ask a question first.'}, status_code=400)

    if not profile_id:
        return JSONResponse({'error': 'Choose a profile first.'}, status_code=400)

    chart = _chart_from_profile(profile_id, owner_email)
    extra = []
    if page in ('dashboard', 'dasha'):
        moon_lon = chart.planets['Moon'].longitude
        birth_date = date.fromisoformat(chart.birth_date)
        mds = calculate_mahadasha(birth_date, moon_lon)
        current = get_current_dasha_periods(mds)
        if current.get('mahadasha'):
            extra.append(f"Current Mahadasha: {current['mahadasha'].lord} ({current['mahadasha'].start} to {current['mahadasha'].end})")
        if current.get('antardasha'):
            extra.append(f"Current Antardasha: {current['antardasha'].lord} ({current['antardasha'].start} to {current['antardasha'].end})")
        if current.get('pratyantardasha'):
            extra.append(f"Current Pratyantardasha: {current['pratyantardasha'].lord} ({current['pratyantardasha'].start} to {current['pratyantardasha'].end})")
    if page in ('dashboard', 'analysis'):
        rulerships = calculate_house_rulerships(chart.ascendant.rashi_index)
        yogas = detect_all_yogas(chart.planets, rulerships)
        doshas = detect_all_doshas(chart.planets)
        extra.append(f"Yogas found: {', '.join(y.name for y in yogas[:6]) if yogas else 'none major'}")
        extra.append(f"Doshas found: {', '.join(d.name for d in doshas[:4]) if doshas else 'none major'}")
    if page == 'vargas':
        vargas = get_varga_signs(chart)
        extra.append(f"D9 Asc: {vargas.get('D9', {}).get('signs', {}).get('Asc', '?')}")
        extra.append(f"D10 Asc: {vargas.get('D10', {}).get('signs', {}).get('Asc', '?')}")
    if page == 'compatibility' and p1 and p2:
        chart1 = _chart_from_profile(int(p1), owner_email)
        chart2 = _chart_from_profile(int(p2), owner_email)
        guna = calculate_guna_milan(chart1.planets['Moon'], chart2.planets['Moon'])
        extra.append(f"Compatibility pair: {chart1.name} + {chart2.name}")
        extra.append(f"Guna Milan total: {guna.get('total_score', 'unknown')}")

    system_prompt, user_prompt = _build_ai_chat_prompt(page, chart, question, '\n'.join(extra))
    answer = ai_generate_reply(system_prompt, user_prompt, owner_email=owner_email)
    return {'answer': answer, 'provider': provider.label}


@app.get("/ai-settings", response_class=HTMLResponse)
async def page_ai_settings(request: Request):
    owner_email = _current_owner_email(request)
    profiles = list_profiles(owner_email)
    config = load_config(owner_email)
    providers_dict = {}
    for k, v in config.items():
        if isinstance(v, AIProvider):
            providers_dict[k] = {
                'name': v.name, 'label': v.label, 'api_key': '', 'has_api_key': bool(v.api_key),
                'model': v.model, 'base_url': v.base_url, 'enabled': v.enabled,
                'max_tokens': v.max_tokens, 'temperature': v.temperature,
            }

    return templates.TemplateResponse("ai_reading.html", {
        "request": request, "page": "ai_reading", "profiles": profiles,
        "profile_id": _get_default_profile_id(owner_email),
        "is_authenticated": _is_authenticated(request),
        "providers": config,
        "providers_json": json.dumps(providers_dict),
        "provider_models_json": json.dumps(PROVIDER_MODELS),
        **_ai_template_state(owner_email),
    })


@app.post("/ai-settings")
async def api_update_ai_settings(request: Request):
    owner_email = _current_owner_email(request)
    data = await request.json()
    provider = data.get('provider')
    model = data.get('model')
    api_key = data.get('api_key')
    enabled = data.get('enabled', False)

    # Disable all providers first
    config = load_config(owner_email)
    for k in config:
        if isinstance(config[k], AIProvider):
            config[k].enabled = False

    # Update and enable selected provider
    if provider in config and isinstance(config[provider], AIProvider):
        config[provider].model = model
        if api_key:
            config[provider].api_key = api_key
        config[provider].enabled = enabled
        save_config(config, owner_email)
        return {'message': f'{config[provider].label} configured and enabled!', 'success': True}

    return {'message': 'Provider not found', 'success': False}


@app.get("/ai-test/{provider_name}")
async def api_test_provider(request: Request, provider_name: str):
    result = test_provider(provider_name, _current_owner_email(request))
    return result


@app.get("/basics", response_class=HTMLResponse)
async def page_basics(request: Request, profile_id: int = Query(None)):
    owner_email = _current_owner_email(request)
    profiles = list_profiles(owner_email)
    pid = profile_id or _get_default_profile_id(owner_email)
    return templates.TemplateResponse("basics.html", {
        "request": request,
        "page": "basics",
        "profiles": profiles,
        "profile_id": pid,
        "is_authenticated": _is_authenticated(request),
        **_ai_template_state(owner_email),
    })


@app.get("/geocode")
async def api_geocode(q: str = Query(...)):
    """Look up coordinates for a place name."""
    results = search_places(q, limit=5)
    return {'results': results}


@app.get("/timezone")
async def api_timezone(lat: float = Query(...), lon: float = Query(...), birth_date: str = Query(None)):
    """Resolve timezone offset for coordinates and optional birth date."""
    target_date = date.fromisoformat(birth_date) if birth_date else None
    return get_tz_offset_for_date(lat, lon, target_date)


@app.post("/transcribe")
async def api_transcribe(audio: UploadFile = File(...)):
    """Transcribe uploaded audio file using local Whisper."""
    try:
        audio_bytes = await audio.read()
        result = transcribe_audio(audio_bytes, audio.filename or 'audio.ogg')
        return result
    except Exception as e:
        raise HTTPException(500, f"Transcription error: {str(e)}")


# ===== HTML PAGE ROUTES =====

def _get_default_profile_id(owner_email: str) -> int:
    """Get first profile ID."""
    profiles = list_profiles(owner_email)
    if not profiles:
        raise HTTPException(404, "No profiles found for this account")
    return profiles[0]['id']


@app.get("/new-profile", response_class=HTMLResponse)
async def page_new_profile(request: Request):
    owner_email = _current_owner_email(request)
    profiles = list_profiles(owner_email)
    return templates.TemplateResponse("new_profile.html", {
        "request": request, "page": "new_profile", "profiles": profiles, "profile_id": None, "is_authenticated": _is_authenticated(request),
        **_ai_template_state(owner_email),
    })


@app.get("/edit/{profile_id}", response_class=HTMLResponse)
async def page_edit_profile(request: Request, profile_id: int):
    owner_email = _current_owner_email(request)
    profiles = list_profiles(owner_email)
    profile = get_profile(profile_id, owner_email)
    if not profile:
        raise HTTPException(404, "Profile not found")
    return templates.TemplateResponse("edit_profile.html", {
        "request": request, "page": "edit_profile", "profiles": profiles,
        "profile_id": profile_id, "profile": profile, "is_authenticated": _is_authenticated(request),
        **_ai_template_state(owner_email),
    })


@app.put("/profiles/{profile_id}")
async def api_update_profile(request: Request, profile_id: int, data: ProfileCreate):
    """Update a profile's birth data."""
    updated = update_profile(
        profile_id,
        owner_email=_current_owner_email(request),
        name=data.name, birth_date=data.birth_date, birth_time=data.birth_time,
        birth_place=data.birth_place, latitude=data.latitude, longitude=data.longitude,
        tz_offset=data.tz_offset, notes=data.notes,
    )
    if updated:
        return {'message': f'Profile updated', 'id': profile_id}
    raise HTTPException(404, "Profile not found")


def _serialize_chart_for_json(chart) -> dict:
    """Serialize chart for JavaScript consumption."""
    planets = {}
    for name, p in chart.planets.items():
        planets[name] = {
            'rashi': p.rashi, 'rashi_index': p.rashi_index,
            'nakshatra': p.nakshatra, 'pada': p.pada,
            'house': p.house, 'retrograde': p.retrograde,
            'degree_in_sign': round(p.degree_in_sign, 4),
            'degree_formatted': deg_to_dms(p.degree_in_sign),
        }
    return planets


def _build_dashboard_payload(chart) -> dict:
    serial = _serialize_chart(chart)

    moon_lon = chart.planets['Moon'].longitude
    birth_date = date.fromisoformat(chart.birth_date)
    mds = calculate_mahadasha(birth_date, moon_lon)
    current = get_current_dasha_periods(mds)
    kp = calculate_kp_bhava_chalit(chart)
    kp_data = kp_to_dict(kp)
    rulerships = calculate_house_rulerships(chart.ascendant.rashi_index)

    dasha_data = {
        'starting_dasha': get_starting_dasha(moon_lon)[0],
        'mahadashas': _serialize_mahadasha_timeline(mds),
        'current': {},
    }
    if current['mahadasha']:
        dasha_data['current']['mahadasha'] = dasha_to_dict(current['mahadasha'])
        dasha_data['current']['mahadasha']['duration_label'] = _format_duration_label(current['mahadasha'].years)
        current_md = next((md for md in dasha_data['mahadashas'] if md['is_current']), None)
        dasha_data['current']['antardashas'] = current_md['antardashas'] if current_md else []
        dasha_data['current']['mahadasha_blurb'] = _period_blurb(current['mahadasha'].lord, chart, kp, rulerships, 'Mahadasha')
        if current['antardasha']:
            dasha_data['current']['antardasha'] = dasha_to_dict(current['antardasha'])
            dasha_data['current']['antardasha']['duration_label'] = _format_duration_label(current['antardasha'].years)
            current_ad = next((ad for ad in dasha_data['current']['antardashas'] if ad['is_current']), None)
            dasha_data['current']['pratyantardashas'] = current_ad['pratyantardashas'] if current_ad else []
            dasha_data['current']['antardasha_blurb'] = _period_blurb(current['antardasha'].lord, chart, kp, rulerships, 'Antardasha')
        if current['pratyantardasha']:
            dasha_data['current']['pratyantardasha'] = dasha_to_dict(current['pratyantardasha'])
            dasha_data['current']['pratyantardasha']['duration_label'] = _format_duration_label(current['pratyantardasha'].years)
            dasha_data['current']['pratyantardasha_blurb'] = _period_blurb(current['pratyantardasha'].lord, chart, kp, rulerships, 'Pratyantardasha')

    transits = calculate_transits(chart)
    transits_data = {k: transit_to_dict(v) for k, v in transits.items()}
    transit_reading = build_transit_reading(chart, transits)
    vargas = get_varga_signs(chart)
    conjunctions = [conjunction_to_dict(c) for c in find_conjunctions(chart.planets)]
    aspects = [aspect_to_dict(a) for a in find_aspects(chart.planets)]
    yogas = [yoga_to_dict(y) for y in detect_all_yogas(chart.planets, rulerships)]

    return {
        'chart': serial,
        'dasha': dasha_data,
        'transits': transits_data,
        'transit_reading': transit_reading,
        'vargas': vargas,
        'kp': kp_data,
        'conjunctions': conjunctions,
        'aspects': aspects,
        'yogas': yogas,
        'house_rulerships': rulerships,
    }


def _dashboard_export_text(data: dict) -> str:
    chart = data['chart']
    lines = []
    lines.append(f"VEDIC ASTRO EXPORT — {chart['name']}")
    lines.append(f"Birth: {chart['birth_date']} {chart['birth_time']}")
    lines.append(f"Place: {chart['birth_place']}")
    lines.append(f"Ayanamsa: {chart['ayanamsa']:.4f}")
    lines.append("")

    lines.append("D1 FOUNDATION")
    lines.append(f"Ascendant: {chart['ascendant']['rashi']} {chart['ascendant']['degree_formatted']} | Nakshatra {chart['ascendant']['nakshatra']} {chart['ascendant']['pada']}")
    for name, p in chart['planets'].items():
        retro = ' Rx' if p['retrograde'] else ''
        lines.append(f"- {name}: {p['rashi']} {p['degree_formatted']} | Nakshatra {p['nakshatra']} {p['pada']} | H{p['house']} | Lord {p['rashi_lord']}{retro}")
    lines.append("")

    lines.append("CURRENT DASHA")
    current = data['dasha']['current']
    if current.get('mahadasha'):
        lines.append(f"Mahadasha: {current['mahadasha']['lord']} | {current['mahadasha']['start']} -> {current['mahadasha']['end']}")
        if current.get('mahadasha_blurb'):
            lines.append(f"  {current['mahadasha_blurb']}")
    if current.get('antardasha'):
        lines.append(f"Antardasha: {current['antardasha']['lord']} | {current['antardasha']['start']} -> {current['antardasha']['end']}")
        if current.get('antardasha_blurb'):
            lines.append(f"  {current['antardasha_blurb']}")
    lines.append("")

    next_md = next((md for md in data['dasha']['mahadashas'] if md['state'] == 'future'), None)
    if next_md:
        lines.append("NEXT UPCOMING DASHA")
        lines.append(f"Mahadasha: {next_md['lord']} | {next_md['start']} -> {next_md['end']} | {next_md['duration_label']}")
        next_ad = next_md['antardashas'][0] if next_md.get('antardashas') else None
        if next_ad:
            lines.append(f"Antardasha: {next_ad['lord']} | {next_ad['start']} -> {next_ad['end']} | {next_ad['duration_label']}")
        lines.append("")

    lines.append("CURRENT TRANSITS")
    for name, t in data['transits'].items():
        lines.append(f"- {name}: {t['rashi']} {t['degree_formatted']} | H{t['house']} | Orb {t['orb']:+.1f}")
    lines.append("")
    lines.append("TRANSIT READING")
    for item in data['transit_reading']:
        lines.append(f"- {item['planet']}: natal {item['natal_sign']} H{item['natal_house']} -> transit {item['transit_sign']} H{item['transit_house']}")
        lines.append(f"  Summary: {item['summary']}")
        lines.append(f"  Practical: {item['practical']}")
    lines.append("")

    lines.append("D9 NAVAMSHA QUICK VIEW")
    for planet, sign in data['vargas']['D9']['signs'].items():
        lines.append(f"- {planet}: {sign}")
    lines.append("")

    lines.append("KP BHAVA CHALIT")
    for name, p in data['chart']['planets'].items():
        kp_p = data['kp']['planets'][name]
        lines.append(f"- {name}: {p['nakshatra']} {p['pada']} | Sub-lord {kp_p['sub_lord']} | Regular H{p['house']} -> KP H{kp_p['kp_house']}")
    lines.append("Sub-lord house rulerships:")
    for lord, houses in data['kp']['house_rulerships'].items():
        if houses:
            lines.append(f"- {lord}: H" + ', H'.join(str(h) for h in houses))
    lines.append("")

    lines.append("HOUSE RULERSHIPS")
    for planet, houses in data['house_rulerships'].items():
        lines.append(f"- {planet}: rules H" + ', H'.join(str(h) for h in houses) + f" | placed in H{data['chart']['planets'][planet]['house']}")
    lines.append("")

    lines.append("YOGAS")
    if data['yogas']:
        for y in data['yogas']:
            lines.append(f"- {y['name']} | Planets: {' + '.join(y['planets'])} | Strength: {y['strength']}")
            lines.append(f"  {y['description']}")
    else:
        lines.append("- No major yogas detected")
    lines.append("")

    lines.append("CONJUNCTIONS")
    if data['conjunctions']:
        for c in data['conjunctions']:
            tight = ' TIGHT' if c['tight'] else ''
            lines.append(f"- {c['planets'][0]} + {c['planets'][1]} | H{c['house']} | {c['sign']} | Orb {c['orb']}°{tight}")
    else:
        lines.append("- No tight conjunctions found")
    lines.append("")

    lines.append("ASPECTS")
    if data['aspects']:
        for a in data['aspects']:
            applying = ' applying' if a['applying'] else ''
            lines.append(f"- {a['from']} H{a['from_house']} -> {a['to']} H{a['to_house']} | {a['type']} | Orb {a['orb']}°{applying}")
    else:
        lines.append("- No major aspects found")

    return '\n'.join(lines)


def _dasha_export_text(data: dict, chart_name: str) -> str:
    lines = []
    lines.append(f"FULL DASHA EXPORT — {chart_name}")
    lines.append("")
    current = data['dasha']['current']
    lines.append("CURRENT PERIODS")
    if current.get('mahadasha'):
        lines.append(f"Mahadasha: {current['mahadasha']['lord']} | {current['mahadasha']['start']} -> {current['mahadasha']['end']}")
    if current.get('antardasha'):
        lines.append(f"Antardasha: {current['antardasha']['lord']} | {current['antardasha']['start']} -> {current['antardasha']['end']}")
    if current.get('pratyantardasha'):
        lines.append(f"Pratyantardasha: {current['pratyantardasha']['lord']} | {current['pratyantardasha']['start']} -> {current['pratyantardasha']['end']}")
    lines.append("")
    lines.append("FULL MAHADASHA TIMELINE")
    for md in data['dasha']['mahadashas']:
        flag = ' NOW' if md['is_current'] else ''
        lines.append(f"- {md['lord']}: {md['start']} -> {md['end']} | {md['duration_label']} ({md['years']}y){flag}")
        for ad in md['antardashas']:
            ad_flag = ' NOW' if ad['is_current'] else ''
            lines.append(f"  - {ad['lord']}: {ad['start']} -> {ad['end']} | {ad['duration_label']} ({ad['years']:.1f}y){ad_flag}")
            for pd in ad['pratyantardashas']:
                pd_flag = ' NOW' if pd['is_current'] else ''
                lines.append(f"    - {pd['lord']}: {pd['start']} -> {pd['end']} | {pd['duration_label']} ({pd['years']:.2f}y){pd_flag}")
    return '\n'.join(lines)


@app.get("/dashboard", response_class=HTMLResponse)
async def page_dashboard(request: Request, profile_id: int = Query(None)):
    try:
        owner_email = _current_owner_email(request)
        profiles = list_profiles(owner_email)
        if not profiles:
            return RedirectResponse(url="/new-profile", status_code=303)
        pid = profile_id or _get_default_profile_id(owner_email)
        chart = _chart_from_profile(pid, owner_email)
        payload = _build_dashboard_payload(chart)

        return templates.TemplateResponse("dashboard.html", {
            "request": request,
            "page": "dashboard",
            "is_authenticated": _is_authenticated(request),
            "profiles": profiles,
            "profile_id": pid,
            **payload,
            "houses_json": json.dumps(list(range(1, 13))),
            "asc_json": json.dumps({
                'rashi': chart.ascendant.rashi,
                'rashi_index': chart.ascendant.rashi_index,
            }),
            "planets_json": json.dumps(_serialize_chart_for_json(chart)),
            **_ai_template_state(owner_email),
        })
    except Exception as e:
        import traceback
        return HTMLResponse(content=f"<pre>Error: {str(e)}\n\n{traceback.format_exc()}</pre>", status_code=500)


@app.get("/dashboard/export")
async def api_dashboard_export(request: Request, profile_id: int = Query(None)):
    owner_email = _current_owner_email(request)
    profiles = list_profiles(owner_email)
    if not profiles:
        raise HTTPException(404, "No profiles found for this account")
    pid = profile_id or _get_default_profile_id(owner_email)
    chart = _chart_from_profile(pid, owner_email)
    payload = _build_dashboard_payload(chart)
    filename = f"vedic-astro-{chart.name.lower().replace(' ', '-')}-dashboard-export.txt"
    content = _dashboard_export_text(payload)
    return Response(
        content=content,
        media_type="text/plain; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@app.get("/dashboard/export-dasha")
async def api_dashboard_dasha_export(request: Request, profile_id: int = Query(None)):
    owner_email = _current_owner_email(request)
    profiles = list_profiles(owner_email)
    if not profiles:
        raise HTTPException(404, "No profiles found for this account")
    pid = profile_id or _get_default_profile_id(owner_email)
    chart = _chart_from_profile(pid, owner_email)
    payload = _build_dashboard_payload(chart)
    filename = f"vedic-astro-{chart.name.lower().replace(' ', '-')}-full-dasha-export.txt"
    content = _dasha_export_text(payload, chart.name)
    return Response(
        content=content,
        media_type="text/plain; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@app.get("/vargas", response_class=HTMLResponse)
async def page_vargas(request: Request, profile_id: int = Query(None)):
    owner_email = _current_owner_email(request)
    profiles = list_profiles(owner_email)
    if not profiles:
        return RedirectResponse(url="/new-profile", status_code=303)
    pid = profile_id or _get_default_profile_id(owner_email)
    chart = _chart_from_profile(pid, owner_email)
    serial = _serialize_chart(chart)
    vargas = get_varga_signs(chart)

    core_vargas = {}
    topic_vargas = {}
    hidden_vargas = {}
    for varga_id, varga in vargas.items():
        meta = VARGA_META.get(varga_id, {})
        enriched = {**varga, **meta}
        tier = meta.get('tier', 'hidden')
        if tier == 'core':
            core_vargas[varga_id] = enriched
        elif tier == 'topic':
            topic_vargas[varga_id] = enriched
        else:
            hidden_vargas[varga_id] = enriched

    return templates.TemplateResponse("vargas.html", {
        "request": request,
        "page": "vargas",
        "is_authenticated": _is_authenticated(request),
        "profiles": profiles,
        "profile_id": pid,
        "chart": serial,
        "core_vargas": core_vargas,
        "topic_vargas": topic_vargas,
        "hidden_vargas": hidden_vargas,
        **_ai_template_state(owner_email),
    })


@app.get("/dasha", response_class=HTMLResponse)
async def page_dasha(request: Request, profile_id: int = Query(None),
                     level: str = Query(None)):
    owner_email = _current_owner_email(request)
    profiles = list_profiles(owner_email)
    if not profiles:
        return RedirectResponse(url="/new-profile", status_code=303)
    pid = profile_id or _get_default_profile_id(owner_email)
    chart = _chart_from_profile(pid, owner_email)
    serial = _serialize_chart(chart)
    kp = calculate_kp_bhava_chalit(chart)

    moon_lon = chart.planets['Moon'].longitude
    birth_date = date.fromisoformat(chart.birth_date)
    mds = calculate_mahadasha(birth_date, moon_lon)
    current = get_current_dasha_periods(mds)

    dasha_data = {
        'starting_dasha': get_starting_dasha(moon_lon)[0],
        'mahadashas': _serialize_mahadasha_timeline(mds),
        'current': {},
    }
    antardashas = None
    pratyantardashas = None

    if current['mahadasha']:
        dasha_data['current']['mahadasha'] = dasha_to_dict(current['mahadasha'])
        if current['antardasha']:
            dasha_data['current']['antardasha'] = dasha_to_dict(current['antardasha'])
        if current['pratyantardasha']:
            dasha_data['current']['pratyantardasha'] = dasha_to_dict(current['pratyantardasha'])
        if level == 'antardashas' or level == 'pratyantardashas':
            ad_list = calculate_antardasha(current['mahadasha'])
            antardashas = [dasha_to_dict(ad) for ad in ad_list]
            if level == 'pratyantardashas' and current['antardasha']:
                pd_list = calculate_pratyantardasha(current['antardasha'], current['mahadasha'].years)
                pratyantardashas = [dasha_to_dict(pd) for pd in pd_list]

    current_dasha_reading = _build_current_dasha_reading(chart, current, kp)

    jaimini_karakas = calculate_chara_karakas(chart.planets)
    karakamsa = calculate_karakamsa(jaimini_karakas, chart.planets)
    chara_dasha = calculate_chara_dasha(chart.planets, chart.ascendant.rashi_index, birth_date)

    return templates.TemplateResponse("dasha.html", {
        "request": request,
        "page": "dasha",
        "is_authenticated": _is_authenticated(request),
        "profiles": profiles,
        "profile_id": pid,
        "chart": serial,
        "dasha": dasha_data,
        "antardashas": antardashas,
        "pratyantardashas": pratyantardashas,
        "current_dasha_reading": current_dasha_reading,
        "chara_dasha": chara_dasha,
        "chara_dasha_text": interpret_chara_dasha(chara_dasha, karakamsa),
        **_ai_template_state(owner_email),
    })


@app.get("/compatibility", response_class=HTMLResponse)
async def page_compatibility(request: Request, p1: int = Query(None), p2: int = Query(None)):
    owner_email = _current_owner_email(request)
    profiles = list_profiles(owner_email)
    if not profiles:
        return RedirectResponse(url="/new-profile", status_code=303)
    pid1 = p1 or (profiles[0]['id'] if profiles else 1)
    pid2 = p2 or (profiles[1]['id'] if len(profiles) > 1 else pid1)

    guna_milan = None
    synastry = None
    person_1 = {}
    person_2 = {}
    if p1 and p2:
        chart1 = _chart_from_profile(pid1, owner_email)
        chart2 = _chart_from_profile(pid2, owner_email)
        guna_milan = calculate_guna_milan(chart1.planets['Moon'], chart2.planets['Moon'])
        synastry = calculate_synastry(chart1, chart2)
        person_1 = {
            'name': chart1.name,
            'ascendant': chart1.ascendant.rashi,
            'moon_rashi': chart1.planets['Moon'].rashi,
            'moon_nakshatra': chart1.planets['Moon'].nakshatra,
            'sun_rashi': chart1.planets['Sun'].rashi,
        }
        person_2 = {
            'name': chart2.name,
            'ascendant': chart2.ascendant.rashi,
            'moon_rashi': chart2.planets['Moon'].rashi,
            'moon_nakshatra': chart2.planets['Moon'].nakshatra,
            'sun_rashi': chart2.planets['Sun'].rashi,
        }

    return templates.TemplateResponse("compatibility.html", {
        "request": request,
        "page": "compatibility",
        "is_authenticated": _is_authenticated(request),
        "profiles": profiles,
        "profile_id": pid1,
        "p1": pid1,
        "p2": pid2,
        "guna_milan": guna_milan,
        "synastry": synastry,
        "person_1": person_1,
        "person_2": person_2,
        **_ai_template_state(owner_email),
    })


@app.get("/analysis", response_class=HTMLResponse)
async def page_analysis(request: Request, profile_id: int = Query(None)):
    owner_email = _current_owner_email(request)
    profiles = list_profiles(owner_email)
    if not profiles:
        return RedirectResponse(url="/new-profile", status_code=303)
    pid = profile_id or _get_default_profile_id(owner_email)
    chart = _chart_from_profile(pid, owner_email)
    serial = _serialize_chart(chart)

    rulerships = calculate_house_rulerships(chart.ascendant.rashi_index)
    conjs = find_conjunctions(chart.planets)
    asps = find_aspects(chart.planets)
    yogas = detect_all_yogas(chart.planets, rulerships)
    bb = get_planet_bhavat_bhavam(chart.planets, {})
    planet_bb = get_planet_house_from_house_analysis(chart.planets)
    sav = calculate_sarva_ashtakavarga(chart.planets, chart.ascendant.rashi_index)
    shadbala = calculate_shadbala(chart.planets)
    doshas = detect_all_doshas(chart.planets)
    jaimini_karakas = calculate_chara_karakas(chart.planets)
    jaimini_interpretation = get_jaimini_interpretation(jaimini_karakas)
    jaimini_raja_yogas = calculate_jaimini_raja_yoga(jaimini_karakas)
    karakamsa = calculate_karakamsa(jaimini_karakas, chart.planets)
    jaimini_sign_aspects = get_jaimini_sign_aspects(chart.planets)

    return templates.TemplateResponse("analysis.html", {
        "request": request,
        "page": "analysis",
        "is_authenticated": _is_authenticated(request),
        "profiles": profiles,
        "profile_id": pid,
        "chart": serial,
        "house_rulerships": rulerships,
        "conjunctions": [conjunction_to_dict(c) for c in conjs],
        "aspects": [aspect_to_dict(a) for a in asps],
        "yogas": [yoga_to_dict(y) for y in yogas],
        "bhavat_bhavam": bb,
        "planet_bhavat_bhavam": planet_bb,
        "ashtakavarga": sav,
        "shadbala": shadbala,
        "doshas": [dosha_to_dict(d) for d in doshas],
        "jaimini_karakas": jaimini_karakas,
        "jaimini_interpretation": jaimini_interpretation,
        "jaimini_raja_yogas": jaimini_raja_yogas,
        "karakamsa": karakamsa,
        "karakamsa_text": interpret_karakamsa(karakamsa),
        "jaimini_sign_aspects": jaimini_sign_aspects,
        **_ai_template_state(owner_email),
    })


@app.get("/reading", response_class=HTMLResponse)
async def page_reading(request: Request, profile_id: int = Query(None)):
    owner_email = _current_owner_email(request)
    profiles = list_profiles(owner_email)
    if not profiles:
        return RedirectResponse(url="/new-profile", status_code=303)
    pid = profile_id or _get_default_profile_id(owner_email)
    chart = _chart_from_profile(pid, owner_email)
    serial = _serialize_chart(chart)
    rulerships = calculate_house_rulerships(chart.ascendant.rashi_index)

    # Gather all data
    moon_lon = chart.planets['Moon'].longitude
    birth_date = date.fromisoformat(chart.birth_date)
    mds = calculate_mahadasha(birth_date, moon_lon)
    current = get_current_dasha_periods(mds)
    dasha_data = {'current': {}}
    if current['mahadasha']: dasha_data['current']['mahadasha'] = dasha_to_dict(current['mahadasha'])
    if current['antardasha']: dasha_data['current']['antardasha'] = dasha_to_dict(current['antardasha'])
    if current['pratyantardasha']: dasha_data['current']['pratyantardasha'] = dasha_to_dict(current['pratyantardasha'])

    yogas = detect_all_yogas(chart.planets, rulerships)
    doshas = detect_all_doshas(chart.planets)
    sb = calculate_shadbala(chart.planets)
    sav = calculate_sarva_ashtakavarga(chart.planets, chart.ascendant.rashi_index)
    conjs = find_conjunctions(chart.planets)
    asps = find_aspects(chart.planets)
    bb = get_planet_bhavat_bhavam(chart.planets, {})
    vargas = get_varga_signs(chart)
    transits = calculate_transits(chart)
    transits_data = {k: transit_to_dict(v) for k, v in transits.items()}

    # SYNTHESIZE — this is the key step
    synthesis = synthesize(
        chart, rulerships, yogas, doshas, sb, sav,
        dasha_data, transits_data, vargas,
        [conjunction_to_dict(c) for c in conjs],
        asps, bb
    )

    return templates.TemplateResponse("reading.html", {
        "request": request, "page": "reading", "profiles": profiles, "is_authenticated": _is_authenticated(request),
        "profile_id": pid, "chart": serial,
        "synthesis": synthesis,
        **_ai_template_state(owner_email),
    })


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 3000))
    uvicorn.run(app, host="0.0.0.0", port=port)
