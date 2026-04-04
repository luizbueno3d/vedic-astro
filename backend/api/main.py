"""FastAPI application for Vedic astrology calculations."""

import os
import sys
import hmac
import hashlib
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, HTTPException, Request, Query, UploadFile, File, Form

from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from datetime import date
import json

from engine.ephemeris import calculate_chart, deg_to_dms, get_rashi_lord, RASHIS
from engine.charts import get_varga_signs, VARGA_FUNCTIONS, VARGA_META
from engine.kp import calculate_kp_bhava_chalit, kp_to_dict
from engine.jaimini import calculate_chara_karakas, calculate_jaimini_raja_yoga, get_jaimini_interpretation
from engine.dasha import (
    calculate_mahadasha, calculate_antardasha, calculate_pratyantardasha,
    get_current_dasha_periods, dasha_to_dict, get_starting_dasha
)
from engine.transits import calculate_transits, find_sign_changes, transit_to_dict
from engine.aspects import find_conjunctions, find_aspects, conjunction_to_dict, aspect_to_dict
from engine.yogas import detect_all_yogas, yoga_to_dict, calculate_house_rulerships
from engine.bhavat_bhavam import get_all_bhavat_bhavam, get_planet_bhavat_bhavam, get_planet_house_from_house_analysis
from engine.ashtakavarga import calculate_sarva_ashtakavarga, interpret_sav_score
from engine.shadbala import calculate_shadbala
from engine.doshas import detect_all_doshas, dosha_to_dict
from engine.guna_milan import calculate_guna_milan
from engine.reading import generate_reading
from engine.synthesis import synthesize
from engine.llm_reading import generate_llm_reading
from engine.ai_provider import (
    load_config, save_config, get_active_provider, update_provider,
    test_provider, PROVIDER_MODELS,
    DEFAULT_PROVIDERS, AIProvider
)
from engine.geocoding import geocode, search_places
from engine.transcription import transcribe_audio
from data.database import (
    list_profiles, get_profile, add_profile, update_profile,
    delete_profile, seed_default_profiles
)

app = FastAPI(title="Vedic Astro", version="1.0.0")

APP_PASSWORD = os.getenv("APP_PASSWORD", "Luiz1234!")
APP_SESSION_SECRET = os.getenv("APP_SESSION_SECRET", "vedic-astro-session-secret-change-me")
AUTH_COOKIE_NAME = "vedic_astro_auth"
PUBLIC_PATHS = {
    "/login",
    "/api",
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


def _login_redirect() -> RedirectResponse:
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie(AUTH_COOKIE_NAME, path="/")
    response.delete_cookie("vedic_astro_session", path="/")
    return response


def _is_html_request(request: Request) -> bool:
    accept = request.headers.get("accept", "")
    return "text/html" in accept


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
    })
    response.delete_cookie(AUTH_COOKIE_NAME, path="/")
    response.delete_cookie("vedic_astro_session", path="/")
    return response


@app.post("/login")
async def api_login(request: Request, password_form: str = Form(None)):
    password = password_form or ""

    content_type = request.headers.get("content-type", "")
    if not password and "application/json" in content_type:
        data = await request.json()
        password = data.get("password", "")

    if password != APP_PASSWORD:
        if _is_html_request(request):
            return RedirectResponse(url="/login?error=Invalid%20password", status_code=303)
        return JSONResponse({"error": "Invalid password"}, status_code=401)

    if "authenticated" in request.session:
        request.session.pop("authenticated", None)
    if _is_html_request(request):
        response = RedirectResponse(url="/dashboard", status_code=303)
    else:
        response = JSONResponse({"success": True})

    response.set_cookie(
        AUTH_COOKIE_NAME,
        _auth_cookie_value(),
        httponly=True,
        secure=True,
        samesite="lax",
        path="/",
        max_age=60 * 60 * 24 * 14,
    )
    return response


@app.post("/logout")
async def api_logout(request: Request):
    request.session.clear()
    response = JSONResponse({"success": True})
    response.delete_cookie(AUTH_COOKIE_NAME, path="/")
    response.delete_cookie("vedic_astro_session", path="/")
    return response


# --- Profiles ---

@app.get("/profiles")
async def api_list_profiles():
    return list_profiles()


@app.post("/profiles")
async def api_create_profile(data: ProfileCreate):
    pid = add_profile(
        data.name, data.birth_date, data.birth_time,
        data.birth_place, data.latitude, data.longitude,
        data.tz_offset, data.notes
    )
    return {"id": pid, "message": f"Profile '{data.name}' created"}


@app.get("/profiles/{profile_id}")
async def api_get_profile(profile_id: int):
    p = get_profile(profile_id)
    if not p:
        raise HTTPException(404, "Profile not found")
    return p


@app.delete("/profiles/{profile_id}")
async def api_delete_profile(profile_id: int):
    if delete_profile(profile_id):
        return {"message": "Deleted"}
    raise HTTPException(404, "Profile not found")


# --- Chart ---

def _chart_from_birth(data: BirthData):
    return calculate_chart(
        data.year, data.month, data.day, data.hour, data.minute,
        data.latitude, data.longitude, data.name, data.place, data.tz_offset
    )


def _chart_from_profile(profile_id: int):
    p = get_profile(profile_id)
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


@app.post("/chart")
async def api_chart_from_birth(data: BirthData):
    chart = _chart_from_birth(data)
    return _serialize_chart(chart)


@app.get("/chart/{profile_id}")
async def api_chart_from_profile(profile_id: int):
    chart = _chart_from_profile(profile_id)
    return _serialize_chart(chart)


# --- Divisional Charts ---

@app.get("/vargas/{profile_id}")
async def api_vargas(profile_id: int, varga: str = None):
    chart = _chart_from_profile(profile_id)
    all_vargas = get_varga_signs(chart)

    if varga:
        if varga not in all_vargas:
            raise HTTPException(400, f"Unknown varga: {varga}. Options: {list(all_vargas.keys())}")
        return {varga: all_vargas[varga]}

    return all_vargas


# --- KP Bhava Chalit ---

@app.get("/kp/{profile_id}")
async def api_kp(profile_id: int):
    chart = _chart_from_profile(profile_id)
    kp = calculate_kp_bhava_chalit(chart)
    return kp_to_dict(kp)


# --- Dasha ---

@app.get("/dasha/{profile_id}")
async def api_dasha(profile_id: int, level: str = 'all'):
    chart = _chart_from_profile(profile_id)
    moon_lon = chart.planets['Moon'].longitude
    birth_date = date.fromisoformat(chart.birth_date)

    mahadashas = calculate_mahadasha(birth_date, moon_lon)

    if level == 'mahadasha':
        return {'mahadashas': [dasha_to_dict(md) for md in mahadashas]}

    # Find current MD and get its antardashas
    current = get_current_dasha_periods(mahadashas)

    result = {
        'starting_dasha': get_starting_dasha(moon_lon)[0],
        'mahadashas': [dasha_to_dict(md) for md in mahadashas],
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

    return result


# --- Transits ---

@app.get("/transits/{profile_id}")
async def api_transits(profile_id: int, date_str: str = None):
    chart = _chart_from_profile(profile_id)
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
async def api_compatibility(profile_id_1: int, profile_id_2: int):
    chart1 = _chart_from_profile(profile_id_1)
    chart2 = _chart_from_profile(profile_id_2)

    moon1 = chart1.planets['Moon']
    moon2 = chart2.planets['Moon']

    moon_dist = (moon2.rashi_index - moon1.rashi_index) % 12

    return {
        'person_1': chart1.name,
        'person_2': chart2.name,
        'moon_1': {'rashi': moon1.rashi, 'nakshatra': moon1.nakshatra},
        'moon_2': {'rashi': moon2.rashi, 'nakshatra': moon2.nakshatra},
        'moon_distance': moon_dist,
        'ascendant_1': chart1.ascendant.rashi,
        'ascendant_2': chart2.ascendant.rashi,
        'interpretation': _moon_distance_interpretation(moon_dist),
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
async def api_aspects(profile_id: int):
    chart = _chart_from_profile(profile_id)
    conjs = find_conjunctions(chart.planets)
    asps = find_aspects(chart.planets)
    return {
        'conjunctions': [conjunction_to_dict(c) for c in conjs],
        'aspects': [aspect_to_dict(a) for a in asps],
    }


@app.get("/yogas/{profile_id}")
async def api_yogas(profile_id: int):
    chart = _chart_from_profile(profile_id)
    rulerships = calculate_house_rulerships(chart.ascendant.rashi_index)
    yogas = detect_all_yogas(chart.planets, rulerships)
    return {
        'yogas': [yoga_to_dict(y) for y in yogas],
        'house_rulerships': {k: v for k, v in rulerships.items()},
    }


@app.get("/bhavat-bhavam/{profile_id}")
async def api_bhavat_bhavam(profile_id: int):
    chart = _chart_from_profile(profile_id)
    bb = get_planet_bhavat_bhavam(chart.planets, {})
    planet_bb = get_planet_house_from_house_analysis(chart.planets)
    return {'bhavat_bhavam': bb, 'planet_bhavat_bhavam': planet_bb}


@app.get("/jaimini/{profile_id}")
async def api_jaimini(profile_id: int):
    chart = _chart_from_profile(profile_id)
    karakas = calculate_chara_karakas(chart.planets)
    return {
        'karakas': karakas,
        'interpretation': get_jaimini_interpretation(karakas),
        'raja_yogas': calculate_jaimini_raja_yoga(karakas),
    }


@app.get("/doshas/{profile_id}")
async def api_doshas(profile_id: int):
    chart = _chart_from_profile(profile_id)
    doshas = detect_all_doshas(chart.planets)
    return {'doshas': [dosha_to_dict(d) for d in doshas]}


@app.get("/reading/{profile_id}")
async def api_reading(profile_id: int):
    chart = _chart_from_profile(profile_id)
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
async def api_llm_reading(profile_id: int):
    """Generate an AI-powered reading using the configured provider."""
    chart = _chart_from_profile(profile_id)
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

    provider = get_active_provider()
    provider_name = provider.label if provider else 'none'

    llm_text = generate_llm_reading(
        chart, rulerships, yogas, doshas, sb, sav,
        dasha_data, transits_data, vargas,
        [conjunction_to_dict(c) for c in conjs], [aspect_to_dict(a) for a in asps],
    )

    return {'reading': llm_text, 'provider': provider_name}


@app.get("/ai-settings", response_class=HTMLResponse)
async def page_ai_settings(request: Request):
    profiles = list_profiles()
    config = load_config()
    providers_dict = {}
    for k, v in config.items():
        if isinstance(v, AIProvider):
            providers_dict[k] = {
                'name': v.name, 'label': v.label, 'api_key': v.api_key[:8] + '...' if v.api_key else '',
                'model': v.model, 'base_url': v.base_url, 'enabled': v.enabled,
                'max_tokens': v.max_tokens, 'temperature': v.temperature,
            }

    return templates.TemplateResponse("ai_reading.html", {
        "request": request, "page": "ai_reading", "profiles": profiles,
        "profile_id": _get_default_profile_id(),
        "is_authenticated": _is_authenticated(request),
        "providers": config,
        "providers_json": json.dumps(providers_dict),
        "provider_models_json": json.dumps(PROVIDER_MODELS),
    })


@app.post("/ai-settings")
async def api_update_ai_settings(request: Request):
    data = await request.json()
    provider = data.get('provider')
    model = data.get('model')
    api_key = data.get('api_key')
    enabled = data.get('enabled', False)

    # Disable all providers first
    config = load_config()
    for k in config:
        if isinstance(config[k], AIProvider):
            config[k].enabled = False

    # Update and enable selected provider
    if provider in config and isinstance(config[provider], AIProvider):
        config[provider].model = model
        if api_key:
            config[provider].api_key = api_key
        config[provider].enabled = enabled
        save_config(config)
        return {'message': f'{config[provider].label} configured and enabled!', 'success': True}

    return {'message': 'Provider not found', 'success': False}


@app.get("/ai-test/{provider_name}")
async def api_test_provider(provider_name: str):
    result = test_provider(provider_name)
    return result


@app.get("/basics", response_class=HTMLResponse)
async def page_basics(request: Request, profile_id: int = Query(None)):
    profiles = list_profiles()
    pid = profile_id or _get_default_profile_id()
    return templates.TemplateResponse("basics.html", {
        "request": request,
        "page": "basics",
        "profiles": profiles,
        "profile_id": pid,
        "is_authenticated": _is_authenticated(request),
    })


@app.get("/geocode")
async def api_geocode(q: str = Query(...)):
    """Look up coordinates for a place name."""
    results = search_places(q, limit=5)
    return {'results': results}


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

def _get_default_profile_id() -> int:
    """Get first profile ID."""
    profiles = list_profiles()
    return profiles[0]['id'] if profiles else 1


@app.get("/new-profile", response_class=HTMLResponse)
async def page_new_profile(request: Request):
    profiles = list_profiles()
    return templates.TemplateResponse("new_profile.html", {
        "request": request, "page": "new_profile", "profiles": profiles, "profile_id": None, "is_authenticated": _is_authenticated(request),
    })


@app.get("/edit/{profile_id}", response_class=HTMLResponse)
async def page_edit_profile(request: Request, profile_id: int):
    profiles = list_profiles()
    profile = get_profile(profile_id)
    if not profile:
        raise HTTPException(404, "Profile not found")
    return templates.TemplateResponse("edit_profile.html", {
        "request": request, "page": "edit_profile", "profiles": profiles,
        "profile_id": profile_id, "profile": profile, "is_authenticated": _is_authenticated(request),
    })


@app.put("/profiles/{profile_id}")
async def api_update_profile(profile_id: int, data: ProfileCreate):
    """Update a profile's birth data."""
    updated = update_profile(
        profile_id,
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


@app.get("/dashboard", response_class=HTMLResponse)
async def page_dashboard(request: Request, profile_id: int = Query(None)):
    try:
        profiles = list_profiles()
        pid = profile_id or _get_default_profile_id()
        chart = _chart_from_profile(pid)
        serial = _serialize_chart(chart)

        # Dasha
        moon_lon = chart.planets['Moon'].longitude
        birth_date = date.fromisoformat(chart.birth_date)
        mds = calculate_mahadasha(birth_date, moon_lon)
        current = get_current_dasha_periods(mds)

        dasha_data = {
            'starting_dasha': get_starting_dasha(moon_lon)[0],
            'mahadashas': [dasha_to_dict(md) for md in mds],
            'current': {},
        }
        if current['mahadasha']:
            dasha_data['current']['mahadasha'] = dasha_to_dict(current['mahadasha'])
            if current['antardasha']:
                dasha_data['current']['antardasha'] = dasha_to_dict(current['antardasha'])
            if current['pratyantardasha']:
                dasha_data['current']['pratyantardasha'] = dasha_to_dict(current['pratyantardasha'])

        # Transits
        transits = calculate_transits(chart)
        transits_data = {k: transit_to_dict(v) for k, v in transits.items()}

        # Vargas
        vargas = get_varga_signs(chart)

        # KP Bhava Chalit
        kp = calculate_kp_bhava_chalit(chart)
        kp_data = kp_to_dict(kp)

        # Aspects & Yogas
        conjs = find_conjunctions(chart.planets)
        asps = find_aspects(chart.planets)
        rulerships = calculate_house_rulerships(chart.ascendant.rashi_index)
        yogas = detect_all_yogas(chart.planets, rulerships)

        return templates.TemplateResponse("dashboard.html", {
            "request": request,
            "page": "dashboard",
            "is_authenticated": _is_authenticated(request),
            "profiles": profiles,
            "profile_id": pid,
            "chart": serial,
            "dasha": dasha_data,
            "transits": transits_data,
            "vargas": vargas,
            "kp": kp_data,
            "conjunctions": [conjunction_to_dict(c) for c in conjs],
            "aspects": [aspect_to_dict(a) for a in asps],
            "yogas": [yoga_to_dict(y) for y in yogas],
            "house_rulerships": rulerships,
            "houses_json": json.dumps(list(range(1, 13))),
            "asc_json": json.dumps({
                'rashi': chart.ascendant.rashi,
                'rashi_index': chart.ascendant.rashi_index,
            }),
            "planets_json": json.dumps(_serialize_chart_for_json(chart)),
        })
    except Exception as e:
        import traceback
        return HTMLResponse(content=f"<pre>Error: {str(e)}\n\n{traceback.format_exc()}</pre>", status_code=500)


@app.get("/vargas", response_class=HTMLResponse)
async def page_vargas(request: Request, profile_id: int = Query(None)):
    profiles = list_profiles()
    pid = profile_id or _get_default_profile_id()
    chart = _chart_from_profile(pid)
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
    })


@app.get("/dasha", response_class=HTMLResponse)
async def page_dasha(request: Request, profile_id: int = Query(None),
                     level: str = Query(None)):
    profiles = list_profiles()
    pid = profile_id or _get_default_profile_id()
    chart = _chart_from_profile(pid)
    serial = _serialize_chart(chart)

    moon_lon = chart.planets['Moon'].longitude
    birth_date = date.fromisoformat(chart.birth_date)
    mds = calculate_mahadasha(birth_date, moon_lon)
    current = get_current_dasha_periods(mds)

    dasha_data = {
        'starting_dasha': get_starting_dasha(moon_lon)[0],
        'mahadashas': [dasha_to_dict(md) for md in mds],
        'current': {},
    }
    antardashas = None
    pratyantardashas = None

    if current['mahadasha']:
        dasha_data['current']['mahadasha'] = dasha_to_dict(current['mahadasha'])
        if level == 'antardashas' or level == 'pratyantardashas':
            ad_list = calculate_antardasha(current['mahadasha'])
            antardashas = [dasha_to_dict(ad) for ad in ad_list]
            if current['antardasha']:
                dasha_data['current']['antardasha'] = dasha_to_dict(current['antardasha'])
            if level == 'pratyantardashas' and current['antardasha']:
                pd_list = calculate_pratyantardasha(current['antardasha'], current['mahadasha'].years)
                pratyantardashas = [dasha_to_dict(pd) for pd in pd_list]
                if current['pratyantardasha']:
                    dasha_data['current']['pratyantardasha'] = dasha_to_dict(current['pratyantardasha'])

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
    })


@app.get("/compatibility", response_class=HTMLResponse)
async def page_compatibility(request: Request, p1: int = Query(None), p2: int = Query(None)):
    profiles = list_profiles()
    pid1 = p1 or (profiles[0]['id'] if profiles else 1)
    pid2 = p2 or (profiles[1]['id'] if len(profiles) > 1 else pid1)

    guna_milan = None
    person_1 = {}
    person_2 = {}
    if p1 and p2:
        chart1 = _chart_from_profile(pid1)
        chart2 = _chart_from_profile(pid2)
        guna_milan = calculate_guna_milan(
            chart1.planets['Moon'].rashi_index,
            chart2.planets['Moon'].rashi_index
        )
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
        "person_1": person_1,
        "person_2": person_2,
    })


@app.get("/analysis", response_class=HTMLResponse)
async def page_analysis(request: Request, profile_id: int = Query(None)):
    profiles = list_profiles()
    pid = profile_id or _get_default_profile_id()
    chart = _chart_from_profile(pid)
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
    })


@app.get("/reading", response_class=HTMLResponse)
async def page_reading(request: Request, profile_id: int = Query(None)):
    profiles = list_profiles()
    pid = profile_id or _get_default_profile_id()
    chart = _chart_from_profile(pid)
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
    })


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 3000))
    uvicorn.run(app, host="0.0.0.0", port=port)
