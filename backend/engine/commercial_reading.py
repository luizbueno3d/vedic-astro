"""Deterministic commercial reading snapshot builder.

This module prepares the factual, stored-ready structure for the first paid
reading product. It does not call AI, does not check payment, and does not write
orders. Its output is intended to become the calculation/content snapshot that a
paid generated reading can later persist and render to PDF.
"""

from __future__ import annotations

from datetime import date

from .ashtakavarga import calculate_sarva_ashtakavarga
from .charts import get_varga_signs
from .dasha import calculate_antardasha, calculate_mahadasha, calculate_pratyantardasha, get_starting_dasha
from .doshas import detect_all_doshas
from .ephemeris import ChartData, deg_to_dms
from .jaimini import calculate_chara_karakas, calculate_jaimini_raja_yoga, calculate_karakamsa
from .kp import calculate_kp_bhava_chalit, kp_to_dict
from .shadbala import calculate_shadbala
from .yogas import calculate_house_rulerships, detect_all_yogas

try:
    from i18n import normalize_locale
except ImportError:  # pragma: no cover - package import path fallback
    from ..i18n import normalize_locale


PRODUCT_CODE = 'life_map'
TEMPLATE_VERSION = 'life_map_v1'

SUPPORTED_READING_LOCALES = {'en', 'pt-BR'}

COPY = {
    'en': {
        'title': 'Life Map Reading',
        'subtitle': 'A structured Vedic astrology life map generated from verified chart calculations.',
        'birth_confirmation': 'Birth Data Confirmation',
        'method': 'How This Reading Works',
        'd1_foundation': 'D1 Foundation',
        'identity': 'Core Identity and Life Pattern',
        'kp_shifts': 'KP / Bhava Chalit Lived Shifts',
        'timing': 'Current Mahadasha / Antardasha',
        'key_placements': 'Important Planetary Placements',
        'jaimini': 'Jaimini Soul and Work Indicators',
        'strengths_tensions': 'Strengths and Tensions',
        'guidance': 'Practical Guidance',
        'conclusion': 'Life Map Summary',
        'method_text': (
            'D1 / Rashi chart (main birth chart) is treated as the foundation. '
            'KP / Bhava Chalit (house-adjusted chart showing where results may shift in lived experience) is read as refinement, not replacement. '
            'D9 / Navamsha and D10 / Dashamsha are confirmation layers. '
            'Jaimini indicators are used for soul direction and worldly execution.'
        ),
        'kp_no_shift': 'No major KP house shift is shown for the highlighted planets.',
        'current_period_none': 'No current Vimshottari dasha period could be identified for the selected date.',
    },
    'pt-BR': {
        'title': 'Mapa de Vida Védico',
        'subtitle': 'Uma leitura védica estruturada gerada a partir de cálculos astrológicos verificados.',
        'birth_confirmation': 'Confirmação dos Dados de Nascimento',
        'method': 'Como Esta Leitura Funciona',
        'd1_foundation': 'Fundação do D1',
        'identity': 'Identidade Central e Padrão de Vida',
        'kp_shifts': 'Mudanças Vividas pelo KP / Bhava Chalit',
        'timing': 'Mahadasha / Antardasha Atual',
        'key_placements': 'Posicionamentos Planetários Importantes',
        'jaimini': 'Indicadores de Alma e Trabalho em Jaimini',
        'strengths_tensions': 'Forças e Tensões',
        'guidance': 'Orientação Prática',
        'conclusion': 'Resumo do Mapa de Vida',
        'method_text': (
            'D1 / Rashi (mapa principal de nascimento) é tratado como a base. '
            'KP / Bhava Chalit (mapa ajustado por casas que mostra onde os resultados podem se deslocar na vida real) é lido como refinamento, não substituição. '
            'D9 / Navamsha e D10 / Dashamsha são camadas de confirmação. '
            'Os indicadores de Jaimini são usados para direção da alma e execução no mundo.'
        ),
        'kp_no_shift': 'Nenhuma mudança importante de casa pelo KP aparece nos planetas destacados.',
        'current_period_none': 'Nenhum período atual de Vimshottari dasha pôde ser identificado para a data selecionada.',
    },
}


def _locale(locale: str | None) -> str:
    normalized = normalize_locale(locale)
    return normalized if normalized in SUPPORTED_READING_LOCALES else 'en'


def _planet_dict(planet) -> dict:
    return {
        'name': planet.name,
        'rashi': planet.rashi,
        'rashi_index': planet.rashi_index,
        'house': planet.house,
        'nakshatra': planet.nakshatra,
        'nakshatra_index': planet.nakshatra_index,
        'pada': planet.pada,
        'degree_in_sign': round(planet.degree_in_sign, 4),
        'degree_formatted': deg_to_dms(planet.degree_in_sign),
        'longitude': round(planet.longitude, 4),
        'retrograde': planet.retrograde,
    }


def _period_dict(period, as_of: date) -> dict | None:
    if not period:
        return None
    return {
        'lord': period.lord,
        'level': period.level,
        'start': period.start.isoformat(),
        'end': period.end.isoformat(),
        'years': round(period.years, 2),
        'is_current': period.start <= as_of <= period.end,
    }


def _current_dasha_at(mahadashas: list, as_of: date) -> dict:
    current = {'mahadasha': None, 'antardasha': None, 'pratyantardasha': None}

    for md in mahadashas:
        if md.start <= as_of <= md.end:
            current['mahadasha'] = md
            for ad in calculate_antardasha(md):
                if ad.start <= as_of <= ad.end:
                    current['antardasha'] = ad
                    for pd in calculate_pratyantardasha(ad, md.years):
                        if pd.start <= as_of <= pd.end:
                            current['pratyantardasha'] = pd
                            break
                    break
            break

    return {
        'mahadasha': _period_dict(current['mahadasha'], as_of),
        'antardasha': _period_dict(current['antardasha'], as_of),
        'pratyantardasha': _period_dict(current['pratyantardasha'], as_of),
    }


def _profile_snapshot(chart: ChartData, profile: dict | None = None) -> dict:
    return {
        'profile_id': profile.get('id') if profile else None,
        'name': profile.get('name') if profile and profile.get('name') else chart.name,
        'birth_date': profile.get('birth_date') if profile and profile.get('birth_date') else chart.birth_date,
        'birth_time': profile.get('birth_time') if profile and profile.get('birth_time') else chart.birth_time,
        'birth_place': profile.get('birth_place') if profile and profile.get('birth_place') else chart.birth_place,
        'latitude': profile.get('latitude') if profile and profile.get('latitude') is not None else chart.latitude,
        'longitude': profile.get('longitude') if profile and profile.get('longitude') is not None else chart.longitude,
        'tz_offset': profile.get('tz_offset') if profile else None,
        'notes': profile.get('notes') if profile else None,
    }


def _jaimini_indicator(role: str, karakas: dict, chart: ChartData, kp, vargas: dict) -> dict | None:
    data = karakas.get(role)
    if not data:
        return None

    planet_name = data['planet']
    planet = chart.planets.get(planet_name)
    kp_placement = kp.planets.get(planet_name)
    return {
        'role': role,
        'planet': planet_name,
        'sign': data['sign'],
        'sign_index': data['sign_index'],
        'house': data['house'],
        'nakshatra': data['nakshatra'],
        'pada': data['pada'],
        'degree_in_sign': round(data['degree'], 4),
        'degree_formatted': deg_to_dms(data['degree']),
        'retrograde': data.get('retrograde', False),
        'd1_house': planet.house if planet else data['house'],
        'kp_house': kp_placement.kp_house if kp_placement else None,
        'd9_sign': vargas.get('D9', {}).get('signs', {}).get(planet_name),
        'meaning': (
            'soul significator, deepest life direction, core karmic lesson'
            if role == 'Atmakaraka'
            else 'career/work significator, vocation, execution, money-making pathway'
        ),
    }


def _jaimini_snapshot(chart: ChartData, kp, vargas: dict) -> dict:
    karakas = calculate_chara_karakas(chart.planets)
    atma = _jaimini_indicator('Atmakaraka', karakas, chart, kp, vargas)
    amatya = _jaimini_indicator('Amatyakaraka', karakas, chart, kp, vargas)
    return {
        'method': '7 classical Chara Karakas by highest degree within sign; nodes excluded.',
        'atma_karaka': atma,
        'amatya_karaka': amatya,
        'all_karakas': karakas,
        'raja_yogas': calculate_jaimini_raja_yoga(karakas),
        'karakamsa': calculate_karakamsa(karakas, chart.planets),
    }


def _kp_shifts(chart: ChartData, kp) -> list[dict]:
    shifts = []
    for name, planet in chart.planets.items():
        kp_house = kp.planets[name].kp_house
        if planet.house == kp_house:
            continue
        shifts.append({
            'planet': name,
            'd1_house': planet.house,
            'kp_house': kp_house,
            'sign': planet.rashi,
            'nakshatra': planet.nakshatra,
            'pada': planet.pada,
            'sub_lord': kp.planets[name].sub_lord,
        })
    return shifts


def _strengths_tensions(chart: ChartData, rulerships: dict) -> dict:
    yogas = detect_all_yogas(chart.planets, rulerships)
    doshas = detect_all_doshas(chart.planets)
    shadbala = calculate_shadbala(chart.planets)
    ashtakavarga = calculate_sarva_ashtakavarga(chart.planets, chart.ascendant.rashi_index)
    return {
        'strongest_planets': shadbala.get('ranking', [])[:3],
        'notable_yogas': [
            {'name': yoga.name, 'strength': yoga.strength, 'planets': yoga.planets}
            for yoga in yogas[:6]
        ],
        'notable_doshas': [
            {'name': dosha.name, 'severity': dosha.severity}
            for dosha in doshas[:6]
        ],
        'ashtakavarga_house_scores': ashtakavarga.get('house_scores', {}),
    }


def _highlighted_planets(chart: ChartData, current_dasha: dict, jaimini: dict) -> list[str]:
    names = ['Sun', 'Moon']
    for period_key in ('mahadasha', 'antardasha'):
        period = current_dasha.get(period_key)
        if period:
            names.append(period['lord'])
    for key in ('atma_karaka', 'amatya_karaka'):
        indicator = jaimini.get(key)
        if indicator:
            names.append(indicator['planet'])
    return list(dict.fromkeys(name for name in names if name in chart.planets))


def _line_for_indicator(indicator: dict | None, locale: str) -> str:
    if not indicator:
        return ''
    if locale == 'pt-BR':
        return (
            f"{indicator['role']}: {indicator['planet']} em {indicator['sign']}, "
            f"nakshatra {indicator['nakshatra']} pada {indicator['pada']}, "
            f"D1 H{indicator['d1_house']} -> KP H{indicator['kp_house']}."
        )
    return (
        f"{indicator['role']}: {indicator['planet']} in {indicator['sign']}, "
        f"nakshatra {indicator['nakshatra']} pada {indicator['pada']}, "
        f"D1 H{indicator['d1_house']} -> KP H{indicator['kp_house']}."
    )


def _build_content(snapshot: dict, locale: str) -> dict:
    copy = COPY[locale]
    profile = snapshot['profile_snapshot']
    calculation = snapshot['calculation_snapshot']
    d1 = calculation['d1']
    current = calculation['current_dasha']
    jaimini = snapshot['jaimini_snapshot']
    strengths = calculation['strengths_tensions']
    kp_shifts = calculation['kp_bhava_chalit']['house_shifts']

    asc = d1['ascendant']
    moon = d1['planets']['Moon']
    sun = d1['planets']['Sun']

    if locale == 'pt-BR':
        birth_intro = f"{profile['name']} nasceu em {profile['birth_date']} às {profile['birth_time']} em {profile['birth_place']}."
        d1_intro = f"Ascendente em {asc['rashi']} no nakshatra {asc['nakshatra']} pada {asc['pada']}; Lua em {moon['rashi']} H{moon['house']}; Sol em {sun['rashi']} H{sun['house']}."
        identity = f"O padrão inicial vem do Ascendente em {asc['rashi']} e da Lua em {moon['rashi']}. O Sol em H{sun['house']} mostra como propósito e visibilidade entram na vida."
        timing = _timing_pt(current, copy)
        guidance = _guidance_pt(current, jaimini)
        conclusion = f"Este mapa coloca {asc['rashi']} como porta de entrada da vida, {moon['rashi']} como clima emocional e {jaimini['atma_karaka']['planet']} como fio condutor da direção da alma."
    else:
        birth_intro = f"{profile['name']} was born on {profile['birth_date']} at {profile['birth_time']} in {profile['birth_place']}."
        d1_intro = f"Ascendant in {asc['rashi']} in {asc['nakshatra']} pada {asc['pada']}; Moon in {moon['rashi']} H{moon['house']}; Sun in {sun['rashi']} H{sun['house']}."
        identity = f"The first life pattern comes through the {asc['rashi']} Ascendant and {moon['rashi']} Moon. The Sun in H{sun['house']} shows how purpose and visibility enter the life."
        timing = _timing_en(current, copy)
        guidance = _guidance_en(current, jaimini)
        conclusion = f"This map places {asc['rashi']} as the life doorway, {moon['rashi']} as the emotional climate, and {jaimini['atma_karaka']['planet']} as the thread of soul direction."

    shift_bullets = [
        (
            f"{item['planet']}: D1 H{item['d1_house']} -> KP H{item['kp_house']} ({item['sign']}, {item['nakshatra']} pada {item['pada']})"
        )
        for item in kp_shifts[:8]
    ] or [copy['kp_no_shift']]

    key_bullets = [
        f"{name}: {planet['rashi']} H{planet['house']}, {planet['nakshatra']} pada {planet['pada']}"
        for name, planet in calculation['key_placements'].items()
    ]

    strength_bullets = []
    for item in strengths['strongest_planets']:
        strength_bullets.append(f"{item['planet']}: {item['score']:.3f}")
    for item in strengths['notable_yogas'][:3]:
        strength_bullets.append(f"{item['name']} ({item['strength']})")
    for item in strengths['notable_doshas'][:3]:
        strength_bullets.append(f"{item['name']} ({item['severity']})")

    sections = [
        {'code': 'birth_confirmation', 'title': copy['birth_confirmation'], 'paragraphs': [birth_intro], 'bullets': []},
        {'code': 'method', 'title': copy['method'], 'paragraphs': [copy['method_text']], 'bullets': []},
        {'code': 'd1_foundation', 'title': copy['d1_foundation'], 'paragraphs': [d1_intro], 'bullets': []},
        {'code': 'identity', 'title': copy['identity'], 'paragraphs': [identity], 'bullets': []},
        {'code': 'kp_shifts', 'title': copy['kp_shifts'], 'paragraphs': [], 'bullets': shift_bullets},
        {'code': 'timing', 'title': copy['timing'], 'paragraphs': [timing], 'bullets': []},
        {'code': 'key_placements', 'title': copy['key_placements'], 'paragraphs': [], 'bullets': key_bullets},
        {
            'code': 'jaimini',
            'title': copy['jaimini'],
            'paragraphs': [
                _line_for_indicator(jaimini.get('atma_karaka'), locale),
                _line_for_indicator(jaimini.get('amatya_karaka'), locale),
            ],
            'bullets': [],
        },
        {'code': 'strengths_tensions', 'title': copy['strengths_tensions'], 'paragraphs': [], 'bullets': strength_bullets},
        {'code': 'guidance', 'title': copy['guidance'], 'paragraphs': [guidance], 'bullets': []},
        {'code': 'conclusion', 'title': copy['conclusion'], 'paragraphs': [conclusion], 'bullets': []},
    ]

    return {
        'title': copy['title'],
        'subtitle': copy['subtitle'],
        'sections': sections,
    }


def _timing_en(current: dict, copy: dict) -> str:
    md = current.get('mahadasha')
    ad = current.get('antardasha')
    if not md:
        return copy['current_period_none']
    text = f"The current Mahadasha (major planetary life period) is {md['lord']} from {md['start']} to {md['end']}."
    if ad:
        text += f" The current Antardasha (sub-period within the Mahadasha) is {ad['lord']} from {ad['start']} to {ad['end']}."
    return text


def _timing_pt(current: dict, copy: dict) -> str:
    md = current.get('mahadasha')
    ad = current.get('antardasha')
    if not md:
        return copy['current_period_none']
    text = f"O Mahadasha atual (grande período planetário da vida) é de {md['lord']} de {md['start']} até {md['end']}."
    if ad:
        text += f" A Antardasha atual (subperíodo dentro do Mahadasha) é de {ad['lord']} de {ad['start']} até {ad['end']}."
    return text


def _guidance_en(current: dict, jaimini: dict) -> str:
    md = current.get('mahadasha', {}).get('lord')
    ad = current.get('antardasha', {}).get('lord')
    ak = jaimini.get('atma_karaka', {}).get('planet')
    amk = jaimini.get('amatya_karaka', {}).get('planet')
    return (
        f"Use the current {md}/{ad} timing as the practical activation layer. "
        f"Read {ak} as the soul lesson and {amk} as the work/execution pathway. "
        "The commercial narrative should explain how these facts meet in ordinary life rather than listing them as isolated placements."
    )


def _guidance_pt(current: dict, jaimini: dict) -> str:
    md = current.get('mahadasha', {}).get('lord')
    ad = current.get('antardasha', {}).get('lord')
    ak = jaimini.get('atma_karaka', {}).get('planet')
    amk = jaimini.get('amatya_karaka', {}).get('planet')
    return (
        f"Use o período atual {md}/{ad} como camada prática de ativação. "
        f"Leia {ak} como a lição da alma e {amk} como o caminho de trabalho e execução. "
        "A narrativa comercial deve explicar como esses fatos aparecem na vida comum, não apenas listar posições isoladas."
    )


def _markdown(content: dict) -> str:
    lines = [f"# {content['title']}", '', content['subtitle'], '']
    for section in content['sections']:
        lines.append(f"## {section['title']}")
        for paragraph in section.get('paragraphs', []):
            if paragraph:
                lines.extend([paragraph, ''])
        for bullet in section.get('bullets', []):
            lines.append(f"- {bullet}")
        lines.append('')
    return '\n'.join(lines).strip() + '\n'


def build_life_map_snapshot(
    chart: ChartData,
    profile: dict | None = None,
    locale: str | None = 'en',
    as_of: date | None = None,
) -> dict:
    """Build a deterministic, stored-ready Life Map Reading snapshot."""
    selected_locale = _locale(locale)
    as_of = as_of or date.today()

    kp = calculate_kp_bhava_chalit(chart)
    kp_data = kp_to_dict(kp)
    vargas = get_varga_signs(chart)
    rulerships = calculate_house_rulerships(chart.ascendant.rashi_index)
    moon_lon = chart.planets['Moon'].longitude
    birth_date = date.fromisoformat(chart.birth_date)
    mahadashas = calculate_mahadasha(birth_date, moon_lon)
    current_dasha = _current_dasha_at(mahadashas, as_of)
    jaimini = _jaimini_snapshot(chart, kp, vargas)
    highlighted = _highlighted_planets(chart, current_dasha, jaimini)

    calculation_snapshot = {
        'as_of': as_of.isoformat(),
        'ayanamsa': round(chart.ayanamsa, 6),
        'd1': {
            'ascendant': _planet_dict(chart.ascendant),
            'planets': {name: _planet_dict(planet) for name, planet in chart.planets.items()},
            'house_rulerships': rulerships,
        },
        'kp_bhava_chalit': {
            **kp_data,
            'house_shifts': _kp_shifts(chart, kp),
        },
        'vargas': {
            'D9': vargas.get('D9'),
            'D10': vargas.get('D10'),
        },
        'current_dasha': {
            'starting_dasha': get_starting_dasha(moon_lon)[0],
            **current_dasha,
        },
        'key_placements': {
            name: _planet_dict(chart.planets[name])
            for name in highlighted
        },
        'strengths_tensions': _strengths_tensions(chart, rulerships),
    }

    snapshot = {
        'product_code': PRODUCT_CODE,
        'template_version': TEMPLATE_VERSION,
        'locale': selected_locale,
        'profile_snapshot': _profile_snapshot(chart, profile),
        'calculation_snapshot': calculation_snapshot,
        'jaimini_snapshot': jaimini,
    }
    content = _build_content(snapshot, selected_locale)
    snapshot['content_json'] = content
    snapshot['content_markdown'] = _markdown(content)
    return snapshot
