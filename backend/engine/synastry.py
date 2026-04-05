"""Vedic synastry helpers.

This module adds a broader relationship layer on top of Guna Milan by comparing
how each chart activates the other's ascendant, Moon, Venus, and partnership axis.
"""

from .aspects import SPECIAL_ASPECTS
from .yogas import calculate_house_rulerships


HOUSE_TOPICS = {
    1: 'identity and how the person feels seen',
    2: 'money, values, family tone, and speech',
    3: 'communication, effort, and courage',
    4: 'emotional security, home, and private comfort',
    5: 'romance, creativity, joy, and children',
    6: 'stress, duty, friction, and service',
    7: 'partnership, attraction, and one-to-one bonding',
    8: 'intimacy, vulnerability, depth, and transformation',
    9: 'belief, meaning, growth, and guidance',
    10: 'career, responsibility, and public life',
    11: 'friendship, gains, and shared future goals',
    12: 'retreat, sacrifice, distance, and spiritual dissolution',
}

BENEFICS = {'Jupiter', 'Venus', 'Moon', 'Mercury'}
MALEFICS = {'Saturn', 'Mars', 'Rahu', 'Ketu', 'Sun'}
RELATIONSHIP_FOCUS = ['Moon', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'Rahu', 'Ketu', 'Sun']
MANGLIK_HOUSES = {1, 2, 4, 7, 8, 12}


def _planet_tone(name: str) -> str:
    if name in BENEFICS:
        return 'supportive'
    if name in MALEFICS:
        return 'intense'
    return 'mixed'


def _tone_phrase(name: str) -> str:
    phrases = {
        'Moon': 'emotional recognition and mood sensitivity',
        'Venus': 'affection, pleasure, and attraction',
        'Mars': 'heat, desire, impatience, and conflict style',
        'Jupiter': 'trust, wisdom, and stabilizing growth',
        'Saturn': 'pressure, seriousness, loyalty, and delay',
        'Rahu': 'obsession, fascination, and karmic appetite',
        'Ketu': 'distance, detachment, and spiritual strangeness',
        'Sun': 'ego, dignity, and identity force',
        'Mercury': 'conversation and mental rhythm',
    }
    return phrases.get(name, name.lower())


def _overlay_house(from_sign_index: int, to_sign_index: int) -> int:
    return ((from_sign_index - to_sign_index) % 12) + 1


def _overlay_note(planet: str, house: int) -> str:
    if house == 1:
        return f'{planet} lands in the other person\'s 1st house, so it strongly shapes how seen, felt, and personally impacted they feel.'
    if house == 5:
        return f'{planet} lands in the 5th house, increasing romance, attraction, joy, and creative connection.'
    if house == 7:
        return f'{planet} lands in the 7th house, directly activating partnership, attraction, and one-to-one bonding.'
    if house == 8:
        return f'{planet} lands in the 8th house, bringing depth, intensity, vulnerability, and transformational chemistry.'
    if house == 12:
        return f'{planet} lands in the 12th house, which can create sacrifice, distance, secrecy, spiritual pull, or emotional blur.'
    return f'{planet} lands in H{house}, influencing {HOUSE_TOPICS[house]}.'


def _cross_house_distance(from_sign_index: int, to_sign_index: int) -> int:
    return ((to_sign_index - from_sign_index) % 12) + 1


def _cross_aspects(chart_a, chart_b) -> list[dict]:
    aspects = []
    key_targets = {'Moon', 'Venus', 'Mars', 'Jupiter', 'Saturn'}
    for from_name, from_planet in chart_a.planets.items():
        if from_name in ('Rahu', 'Ketu'):
            aspect_distances = [3, 7, 10]
        elif from_name in SPECIAL_ASPECTS:
            aspect_distances = list(set(SPECIAL_ASPECTS[from_name] + [7]))
        else:
            aspect_distances = [7]

        for to_name, to_planet in chart_b.planets.items():
            if to_name not in key_targets and from_name not in key_targets:
                continue
            house_distance = _cross_house_distance(from_planet.rashi_index, to_planet.rashi_index)
            if house_distance not in aspect_distances:
                continue
            aspects.append({
                'from': from_name,
                'to': to_name,
                'from_sign': from_planet.rashi,
                'to_sign': to_planet.rashi,
                'distance': house_distance,
                'note': f"{from_name} from one chart aspects {to_name} in the other chart, linking {_tone_phrase(from_name)} with {_tone_phrase(to_name)}.",
            })
    return aspects


def _cross_conjunctions(chart_a, chart_b, orb_limit: float = 8.0) -> list[dict]:
    conjunctions = []
    for from_name, from_planet in chart_a.planets.items():
        if from_name not in RELATIONSHIP_FOCUS:
            continue
        for to_name, to_planet in chart_b.planets.items():
            if to_name not in RELATIONSHIP_FOCUS:
                continue
            if from_planet.rashi_index != to_planet.rashi_index:
                continue
            orb = abs(from_planet.longitude - to_planet.longitude)
            if orb > 180:
                orb = 360 - orb
            if orb > orb_limit:
                continue
            conjunctions.append({
                'planet_1': from_name,
                'planet_2': to_name,
                'sign': from_planet.rashi,
                'orb': round(orb, 2),
                'note': f"{from_name} and {to_name} meet in {from_planet.rashi}, blending {_tone_phrase(from_name)} with {_tone_phrase(to_name)}.",
            })
    return conjunctions


def _manglik_from_reference(planets: dict, reference_sign_index: int) -> dict:
    mars = planets['Mars']
    house = ((mars.rashi_index - reference_sign_index) % 12) + 1
    return {'house': house, 'active': house in MANGLIK_HOUSES}


def _manglik_report(chart) -> dict:
    asc_check = _manglik_from_reference(chart.planets, chart.ascendant.rashi_index)
    moon_check = _manglik_from_reference(chart.planets, chart.planets['Moon'].rashi_index)
    venus_check = _manglik_from_reference(chart.planets, chart.planets['Venus'].rashi_index)
    hits = sum(1 for item in [asc_check, moon_check, venus_check] if item['active'])
    if hits == 0:
        severity = 'none'
    elif hits == 1:
        severity = 'mild'
    elif hits == 2:
        severity = 'moderate'
    else:
        severity = 'strong'
    return {
        'ascendant': asc_check,
        'moon': moon_check,
        'venus': venus_check,
        'severity': severity,
    }


def _seventh_lord_name(chart) -> str:
    rulerships = calculate_house_rulerships(chart.ascendant.rashi_index)
    for planet, houses in rulerships.items():
        if 7 in houses:
            return planet
    return ''


def _overlay_bundle(source_chart, target_chart, source_name: str, target_name: str) -> list[dict]:
    target_refs = {
        'Asc': target_chart.ascendant.rashi_index,
        'Moon': target_chart.planets['Moon'].rashi_index,
        'Venus': target_chart.planets['Venus'].rashi_index,
    }
    items = []
    for planet_name in RELATIONSHIP_FOCUS:
        planet = source_chart.planets[planet_name]
        for ref_name, ref_sign in target_refs.items():
            house = _overlay_house(planet.rashi_index, ref_sign)
            if house not in {1, 5, 7, 8, 12}:
                continue
            items.append({
                'source': source_name,
                'target': target_name,
                'planet': planet_name,
                'reference': ref_name,
                'house': house,
                'tone': _planet_tone(planet_name),
                'note': _overlay_note(planet_name, house),
            })
    return items


def _partnership_axis_notes(chart_a, chart_b, name_a: str, name_b: str) -> list[dict]:
    notes = []
    lord_b = _seventh_lord_name(chart_b)
    lord_a = _seventh_lord_name(chart_a)
    if lord_b:
        a_venus_to_b_7th_lord = _overlay_house(chart_a.planets['Venus'].rashi_index, chart_b.planets[lord_b].rashi_index)
        notes.append({
            'title': f'{name_a} Venus to {name_b} 7th lord',
            'detail': f"{name_a}'s Venus falls {a_venus_to_b_7th_lord} houses from {name_b}'s 7th lord {lord_b}, linking attraction with partnership expectation.",
        })
    if lord_a:
        b_moon_to_a_7th_lord = _overlay_house(chart_b.planets['Moon'].rashi_index, chart_a.planets[lord_a].rashi_index)
        notes.append({
            'title': f'{name_b} Moon to {name_a} 7th lord',
            'detail': f"{name_b}'s Moon falls {b_moon_to_a_7th_lord} houses from {name_a}'s 7th lord {lord_a}, showing how emotional needs touch the partnership axis.",
        })
    return notes


def _summary_bucket(overlays: list[dict], aspects: list[dict], conjunctions: list[dict], manglik_a: dict, manglik_b: dict) -> dict:
    emotional = []
    chemistry = []
    stability = []
    pressure = []

    for item in overlays:
        text = f"{item['source']} {item['planet']} -> {item['target']} {item['reference']} H{item['house']}: {item['note']}"
        if item['planet'] == 'Moon' or item['reference'] == 'Moon':
            emotional.append(text)
        if item['planet'] in {'Venus', 'Mars', 'Rahu'} or item['house'] in {5, 7, 8}:
            chemistry.append(text)
        if item['planet'] in {'Jupiter', 'Saturn'} or item['house'] in {1, 7}:
            stability.append(text)
        if item['planet'] in {'Saturn', 'Mars', 'Rahu', 'Ketu'} or item['house'] in {8, 12, 6}:
            pressure.append(text)

    for item in conjunctions + aspects:
        text = item['note']
        if 'Moon' in text:
            emotional.append(text)
        if 'Venus' in text or 'Mars' in text or 'Rahu' in text:
            chemistry.append(text)
        if 'Jupiter' in text or 'Saturn' in text:
            stability.append(text)

    if manglik_a['severity'] != 'none' or manglik_b['severity'] != 'none':
        pressure.append(
            f"Manglik interaction: person A is {manglik_a['severity']} and person B is {manglik_b['severity']}. Similar Mars signatures can normalize heat, while mismatched intensity can create conflict style differences."
        )

    return {
        'emotional_fit': emotional[:4],
        'chemistry': chemistry[:4],
        'long_term': stability[:4],
        'pressure_points': pressure[:4],
    }


def calculate_synastry(chart_a, chart_b) -> dict:
    """Build a first strong Vedic synastry layer."""
    overlays = _overlay_bundle(chart_a, chart_b, chart_a.name, chart_b.name)
    overlays += _overlay_bundle(chart_b, chart_a, chart_b.name, chart_a.name)
    aspects = _cross_aspects(chart_a, chart_b) + _cross_aspects(chart_b, chart_a)
    conjunctions = _cross_conjunctions(chart_a, chart_b)
    manglik_a = _manglik_report(chart_a)
    manglik_b = _manglik_report(chart_b)
    partnership_axis = _partnership_axis_notes(chart_a, chart_b, chart_a.name, chart_b.name)
    summary = _summary_bucket(overlays, aspects, conjunctions, manglik_a, manglik_b)

    return {
        'overlays': overlays,
        'cross_aspects': aspects,
        'cross_conjunctions': conjunctions,
        'manglik': {
            'person_1': manglik_a,
            'person_2': manglik_b,
            'compatibility_note': 'Manglik is treated here as heat/intensity style, not as an automatic relationship failure.',
        },
        'partnership_axis': partnership_axis,
        'summary': summary,
    }
