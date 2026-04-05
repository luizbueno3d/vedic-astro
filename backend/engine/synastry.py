"""Vedic synastry helpers.

This module adds a broader relationship layer on top of Guna Milan by comparing
how each chart activates the other's ascendant, Moon, Venus, and partnership axis.
"""

from .aspects import SPECIAL_ASPECTS
from .charts import d9_navamsha
from .shadbala import DEBILITATION, EXALTATION, get_combustion_status, get_sign_relationship
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
KEY_OVERLAY_HOUSES = {1, 4, 5, 7, 8, 12}


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
    if house == 4:
        return f'{planet} lands in the 4th house, influencing emotional comfort, home feeling, and inner safety.'
    if house == 5:
        return f'{planet} lands in the 5th house, increasing romance, attraction, joy, and creative connection.'
    if house == 7:
        return f'{planet} lands in the 7th house, directly activating partnership, attraction, and one-to-one bonding.'
    if house == 8:
        return f'{planet} lands in the 8th house, bringing depth, intensity, vulnerability, and transformational chemistry.'
    if house == 12:
        return f'{planet} lands in the 12th house, which can create sacrifice, distance, secrecy, spiritual pull, or emotional blur.'
    return f'{planet} lands in H{house}, influencing {HOUSE_TOPICS[house]}.'


def _make_signal(key: str, category: str, score: int, title: str, detail: str) -> dict:
    return {
        'key': key,
        'category': category,
        'score': score,
        'title': title,
        'detail': detail,
    }


def _sort_signals(signals: list[dict]) -> list[dict]:
    return sorted(signals, key=lambda item: (-item['score'], item['title']))


def _top_signals(signals: list[dict], category: str, limit: int = 4) -> list[dict]:
    return _sort_signals([s for s in signals if s['category'] == category])[:limit]


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


def _lagna_lord_name(chart) -> str:
    rulerships = calculate_house_rulerships(chart.ascendant.rashi_index)
    for planet, houses in rulerships.items():
        if 1 in houses:
            return planet
    return ''


def _planet_affliction_notes(chart, planet_name: str) -> list[str]:
    planet = chart.planets[planet_name]
    notes = []
    sun_longitude = chart.planets['Sun'].longitude
    relationship = get_sign_relationship(planet_name, planet.rashi_index)
    combustion = get_combustion_status(planet_name, planet.longitude, sun_longitude, planet.retrograde)

    if planet_name in DEBILITATION and planet.rashi_index == DEBILITATION[planet_name]:
        notes.append(f'{planet_name} is debilitated in {planet.rashi}.')
    elif planet_name in EXALTATION and planet.rashi_index == EXALTATION[planet_name]:
        notes.append(f'{planet_name} is exalted in {planet.rashi}.')
    elif relationship == 'enemy':
        notes.append(f'{planet_name} is in an enemy sign ({planet.rashi}).')
    elif relationship == 'friend':
        notes.append(f'{planet_name} is in a friend sign ({planet.rashi}).')

    if combustion == 'combust':
        notes.append(f'{planet_name} is combust, which can weaken clean expression.')

    if planet.retrograde:
        notes.append(f'{planet_name} is retrograde, so its relationship themes can work in an internalized or delayed way.')

    return notes


def _d9_support_notes(chart) -> dict:
    venus_d9 = d9_navamsha(chart.planets['Venus'].longitude)
    jupiter_d9 = d9_navamsha(chart.planets['Jupiter'].longitude)
    lord_7 = _seventh_lord_name(chart)
    lord_7_d9 = d9_navamsha(chart.planets[lord_7].longitude) if lord_7 else ''

    notes = []
    strong_signs = {'Taurus', 'Libra', 'Pisces', 'Sagittarius', 'Cancer'}
    if venus_d9 in strong_signs:
        notes.append(f'Venus is in {venus_d9} in D9, giving decent relationship support in the Navamsha.')
    else:
        notes.append(f'Venus is in {venus_d9} in D9, so D9 support for relationship sweetness needs more nuance.')

    if jupiter_d9 in strong_signs:
        notes.append(f'Jupiter is in {jupiter_d9} in D9, helping wisdom and stabilizing grace in partnership matters.')
    else:
        notes.append(f'Jupiter is in {jupiter_d9} in D9, so long-term guidance in relationship may need conscious development.')

    if lord_7 and lord_7_d9:
        notes.append(f'The 7th lord {lord_7} goes to {lord_7_d9} in D9, which is the key Navamsha checkpoint for marriage promise.')

    return {
        'venus_d9': venus_d9,
        'jupiter_d9': jupiter_d9,
        'seventh_lord_d9': lord_7_d9,
        'notes': notes,
    }


def calculate_natal_relationship_capacity(chart) -> dict:
    """Judge each chart's own relationship capacity before synastry."""
    lord_7 = _seventh_lord_name(chart)
    p7 = chart.planets[lord_7] if lord_7 else None
    venus = chart.planets['Venus']
    jupiter = chart.planets['Jupiter']
    house7_occupants = [name for name, planet in chart.planets.items() if planet.house == 7]
    d9_support = _d9_support_notes(chart)

    strengths = []
    cautions = []
    score = 50

    if p7:
        strengths.append(f'7th lord is {lord_7} in H{p7.house} ({p7.rashi}).')
        if p7.house in {1, 4, 5, 7, 9, 10, 11}:
            score += 10
            strengths.append(f'{lord_7} sits in a more supportive house for partnership expression.')
        elif p7.house in {6, 8, 12}:
            score -= 10
            cautions.append(f'{lord_7} sits in H{p7.house}, which can complicate partnership flow.')
        for note in _planet_affliction_notes(chart, lord_7):
            if 'exalted' in note or 'friend sign' in note:
                score += 6
                strengths.append(note)
            else:
                score -= 6
                cautions.append(note)

    strengths.append(f'Venus is in H{venus.house} ({venus.rashi}) and shows how affection and attraction are expressed.')
    for note in _planet_affliction_notes(chart, 'Venus'):
        if 'exalted' in note or 'friend sign' in note:
            score += 5
            strengths.append(note)
        else:
            score -= 5
            cautions.append(note)

    strengths.append(f'Jupiter is in H{jupiter.house} ({jupiter.rashi}) and shows grace, ethics, and stabilizing capacity in relationship matters.')
    for note in _planet_affliction_notes(chart, 'Jupiter'):
        if 'exalted' in note or 'friend sign' in note:
            score += 4
            strengths.append(note)
        else:
            score -= 4
            cautions.append(note)

    if house7_occupants:
        strengths.append(f'Planets in the 7th house: {", ".join(house7_occupants)}.')
        for occupant in house7_occupants:
            if occupant in BENEFICS:
                score += 4
            elif occupant in {'Saturn', 'Mars', 'Rahu', 'Ketu'}:
                score -= 4
                cautions.append(f'{occupant} in the 7th house adds intensity, delay, or karmic pressure to relationship patterns.')
    else:
        strengths.append('The 7th house is empty, so partnership depends more strongly on the 7th lord and Venus condition.')

    for note in d9_support['notes']:
        if 'decent relationship support' in note or 'helping wisdom' in note:
            score += 5
            strengths.append(note)
        else:
            cautions.append(note)

    score = max(0, min(100, score))
    if score >= 75:
        verdict = 'Strong natal relationship capacity'
    elif score >= 60:
        verdict = 'Good but mixed natal relationship capacity'
    elif score >= 45:
        verdict = 'Moderate natal relationship capacity with clear lessons'
    else:
        verdict = 'Relationship capacity needs conscious work and maturity'

    summary = (
        f"This chart's relationship foundation is judged from the 7th house, the 7th lord {lord_7}, Venus, Jupiter, and D9 support. "
        f"The current reading sees it as: {verdict.lower()}."
    )

    return {
        'score': score,
        'verdict': verdict,
        'summary': summary,
        'seventh_lord': lord_7,
        'seventh_house_occupants': house7_occupants,
        'strengths': strengths[:8],
        'cautions': cautions[:8],
        'd9_support': d9_support,
    }


def _overlay_bundle(source_chart, target_chart, source_name: str, target_name: str) -> list[dict]:
    seventh_house_sign = (target_chart.ascendant.rashi_index + 6) % 12
    seventh_lord = _seventh_lord_name(target_chart)
    target_refs = {
        'Asc': target_chart.ascendant.rashi_index,
        'Moon': target_chart.planets['Moon'].rashi_index,
        '7th House': seventh_house_sign,
    }
    if seventh_lord:
        target_refs['7th Lord'] = target_chart.planets[seventh_lord].rashi_index
    items = []
    for planet_name in RELATIONSHIP_FOCUS:
        planet = source_chart.planets[planet_name]
        for ref_name, ref_sign in target_refs.items():
            house = _overlay_house(planet.rashi_index, ref_sign)
            if house not in KEY_OVERLAY_HOUSES:
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
    lagnesh_a = _lagna_lord_name(chart_a)
    lagnesh_b = _lagna_lord_name(chart_b)
    if lord_b:
        a_venus_to_b_7th_lord = _overlay_house(chart_a.planets['Venus'].rashi_index, chart_b.planets[lord_b].rashi_index)
        a_moon_to_b_7th_lord = _overlay_house(chart_a.planets['Moon'].rashi_index, chart_b.planets[lord_b].rashi_index)
        notes.append({
            'title': f'{name_a} Venus to {name_b} 7th lord',
            'detail': f"{name_a}'s Venus falls {a_venus_to_b_7th_lord} houses from {name_b}'s 7th lord {lord_b}, linking attraction with partnership expectation.",
        })
        notes.append({
            'title': f'{name_a} Moon to {name_b} 7th lord',
            'detail': f"{name_a}'s Moon falls {a_moon_to_b_7th_lord} houses from {name_b}'s 7th lord {lord_b}, showing how emotional needs directly touch {name_b}'s marriage axis.",
        })
    if lord_a:
        b_moon_to_a_7th_lord = _overlay_house(chart_b.planets['Moon'].rashi_index, chart_a.planets[lord_a].rashi_index)
        b_venus_to_a_7th_lord = _overlay_house(chart_b.planets['Venus'].rashi_index, chart_a.planets[lord_a].rashi_index)
        notes.append({
            'title': f'{name_b} Moon to {name_a} 7th lord',
            'detail': f"{name_b}'s Moon falls {b_moon_to_a_7th_lord} houses from {name_a}'s 7th lord {lord_a}, showing how emotional needs touch the partnership axis.",
        })
        notes.append({
            'title': f'{name_b} Venus to {name_a} 7th lord',
            'detail': f"{name_b}'s Venus falls {b_venus_to_a_7th_lord} houses from {name_a}'s 7th lord {lord_a}, showing how attraction and affection interact with {name_a}'s marriage pattern.",
        })

    if lagnesh_a and lagnesh_b:
        distance = _overlay_house(chart_a.planets[lagnesh_a].rashi_index, chart_b.planets[lagnesh_b].rashi_index)
        notes.append({
            'title': f'{name_a} lagna lord to {name_b} lagna lord',
            'detail': f"{lagnesh_a} and {lagnesh_b} show how each person operates in life. Their house distance is {distance}, which helps describe whether identity styles cooperate, complement, or challenge each other.",
        })
    return notes


def _planet_aspects_sign(planet_name: str, from_sign: int, to_sign: int) -> bool:
    if planet_name in ('Rahu', 'Ketu'):
        aspect_distances = [3, 7, 10]
    elif planet_name in SPECIAL_ASPECTS:
        aspect_distances = list(set(SPECIAL_ASPECTS[planet_name] + [7]))
    else:
        aspect_distances = [7]
    distance = ((to_sign - from_sign) % 12) + 1
    return distance in aspect_distances


def _build_seventh_axis_analysis(chart_a, chart_b, name_a: str, name_b: str) -> list[dict]:
    signals = []
    lord_a = _seventh_lord_name(chart_a)
    lord_b = _seventh_lord_name(chart_b)
    if not lord_a or not lord_b:
        return signals

    p7a = chart_a.planets[lord_a]
    p7b = chart_b.planets[lord_b]
    seventh_sign_a = (chart_a.ascendant.rashi_index + 6) % 12
    seventh_sign_b = (chart_b.ascendant.rashi_index + 6) % 12

    # 7th lord to 7th lord direct link
    if p7a.rashi_index == p7b.rashi_index:
        signals.append(_make_signal(
            '7lord-conjunction', 'long_term', 95,
            '7th lord to 7th lord conjunction',
            f"{lord_a} and {lord_b} meet in the same sign, so both charts bring their partnership karma into one field. This is one of the strongest direct marriage-axis links."
        ))
    elif _planet_aspects_sign(lord_a, p7a.rashi_index, p7b.rashi_index) or _planet_aspects_sign(lord_b, p7b.rashi_index, p7a.rashi_index):
        signals.append(_make_signal(
            '7lord-aspect', 'long_term', 84,
            '7th lord to 7th lord aspect',
            f"{lord_a} and {lord_b} aspect each other across the charts, directly linking the two partnership systems even without conjunction."
        ))

    # Planet occupancy / activation of partner's 7th sign
    for src_chart, src_name, target_sign, target_lord, target_name in [
        (chart_a, name_a, seventh_sign_b, lord_b, name_b),
        (chart_b, name_b, seventh_sign_a, lord_a, name_a),
    ]:
        for planet_name in ['Moon', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'Rahu', 'Ketu']:
            p = src_chart.planets[planet_name]
            distance = _overlay_house(p.rashi_index, target_sign)
            if distance == 1:
                category = 'chemistry' if planet_name in {'Venus', 'Mars', 'Rahu'} else 'long_term' if planet_name in {'Jupiter', 'Saturn'} else 'emotional_fit'
                score = {'Venus': 88, 'Moon': 85, 'Jupiter': 83, 'Mars': 76, 'Saturn': 72, 'Rahu': 74, 'Ketu': 65}.get(planet_name, 70)
                signals.append(_make_signal(
                    f'{src_name}-{planet_name}-occupies-{target_name}-7th', category, score,
                    f"{src_name} {planet_name} occupies {target_name}'s 7th house",
                    f"{src_name}'s {planet_name} falls directly into {target_name}'s 7th house, so {_tone_phrase(planet_name)} becomes a direct partnership force in the relationship."
                ))
            elif distance in {5, 7, 8, 12}:
                category = 'chemistry' if distance in {5, 8} else 'pressure_points' if distance == 12 or planet_name in {'Saturn', 'Rahu', 'Ketu'} else 'long_term'
                score = 58 if distance == 12 else 66 if distance == 8 else 62
                signals.append(_make_signal(
                    f'{src_name}-{planet_name}-{target_name}-7th-h{distance}', category, score,
                    f"{src_name} {planet_name} to {target_name}'s 7th axis",
                    f"{src_name}'s {planet_name} falls {distance} houses from {target_name}'s 7th house, so {_tone_phrase(planet_name)} meaningfully colors the partnership axis rather than touching it weakly."
                ))

        # direct conjunction/aspect to partner's 7th lord
        for planet_name in ['Moon', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'Rahu', 'Ketu']:
            p = src_chart.planets[planet_name]
            if p.rashi_index == chart_b.planets[target_lord].rashi_index if src_name == name_a else p.rashi_index == chart_a.planets[target_lord].rashi_index:
                signals.append(_make_signal(
                    f'{src_name}-{planet_name}-conj-{target_name}-7lord',
                    'chemistry' if planet_name in {'Venus', 'Mars', 'Rahu'} else 'emotional_fit' if planet_name == 'Moon' else 'long_term',
                    86,
                    f"{src_name} {planet_name} conjunct {target_name}'s 7th lord",
                    f"{src_name}'s {planet_name} directly conjoins {target_name}'s 7th lord {target_lord}, which is a much stronger partnership signal than a loose house-distance note."
                ))
            target_sign_index = chart_b.planets[target_lord].rashi_index if src_name == name_a else chart_a.planets[target_lord].rashi_index
            if _planet_aspects_sign(planet_name, p.rashi_index, target_sign_index):
                signals.append(_make_signal(
                    f'{src_name}-{planet_name}-aspect-{target_name}-7lord',
                    'pressure_points' if planet_name in {'Saturn', 'Mars', 'Rahu', 'Ketu'} else 'long_term' if planet_name == 'Jupiter' else 'emotional_fit',
                    78,
                    f"{src_name} {planet_name} aspects {target_name}'s 7th lord",
                    f"{src_name}'s {planet_name} aspects {target_name}'s 7th lord {target_lord}, directly modifying how the other person experiences partnership karma."
                ))

    # 7th lord condition itself matters
    for lord, p7, owner_name in [(lord_a, p7a, name_a), (lord_b, p7b, name_b)]:
        notes = _planet_affliction_notes(chart_a if owner_name == name_a else chart_b, lord)
        if p7.house in {6, 8, 12}:
            signals.append(_make_signal(
                f'{owner_name}-7lord-difficult-house', 'pressure_points', 82,
                f"{owner_name}'s 7th lord is in a difficult house",
                f"{owner_name}'s 7th lord {lord} sits in H{p7.house}, so their own partnership system is more effortful before synastry is even considered."
            ))
        if any('exalted' in n or 'friend sign' in n for n in notes):
            signals.append(_make_signal(
                f'{owner_name}-7lord-strong', 'long_term', 79,
                f"{owner_name}'s 7th lord is relatively supported",
                f"{owner_name}'s 7th lord {lord} has supportive condition ({'; '.join(notes)}), which helps the chart sustain partnership better."
            ))
        if any('enemy sign' in n or 'combust' in n or 'debilitated' in n for n in notes):
            signals.append(_make_signal(
                f'{owner_name}-7lord-afflicted', 'pressure_points', 79,
                f"{owner_name}'s 7th lord is afflicted",
                f"{owner_name}'s 7th lord {lord} shows strain ({'; '.join(notes)}), so relationship flow can be pressured from inside the natal chart itself."
            ))

    return signals


def _same_or_trinal(sign_a: str, sign_b: str) -> bool:
    signs = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
    ia = signs.index(sign_a)
    ib = signs.index(sign_b)
    diff = (ib - ia) % 12
    return diff in {0, 4, 8}


def _build_d9_compatibility(chart_a, chart_b, name_a: str, name_b: str) -> dict:
    d9a = _d9_support_notes(chart_a)
    d9b = _d9_support_notes(chart_b)
    signals = []
    if _same_or_trinal(d9a['venus_d9'], d9b['venus_d9']):
        signals.append(_make_signal('d9-venus', 'chemistry', 83, 'D9 Venus harmony', f"D9 Venus placements ({d9a['venus_d9']} and {d9b['venus_d9']}) support a more natural romantic style match."))
    if _same_or_trinal(d9a['jupiter_d9'], d9b['jupiter_d9']):
        signals.append(_make_signal('d9-jupiter', 'long_term', 80, 'D9 Jupiter support', f"D9 Jupiter placements ({d9a['jupiter_d9']} and {d9b['jupiter_d9']}) support shared growth, values, and stabilizing grace."))
    if d9a['seventh_lord_d9'] and d9b['seventh_lord_d9'] and _same_or_trinal(d9a['seventh_lord_d9'], d9b['seventh_lord_d9']):
        signals.append(_make_signal('d9-7lord', 'long_term', 88, 'D9 7th-lord confirmation', f"The D9 7th-lord placements ({d9a['seventh_lord_d9']} and {d9b['seventh_lord_d9']}) support each other, which is a real Navamsha confirmation for partnership durability."))
    summary = 'D9 acts here as confirmation, not replacement. It checks whether the D1 relationship promise is supported at a deeper maturity layer.'
    return {
        'person_1': d9a,
        'person_2': d9b,
        'signals': signals,
        'summary': summary,
    }


def _categorize_overlay_signal(item: dict) -> dict:
    planet = item['planet']
    ref = item['reference']
    house = item['house']
    if planet == 'Moon' and ref == 'Moon':
        category, score = 'emotional_fit', 86 if house in {1, 4, 7} else 74
    elif planet == 'Venus' and house in {5, 7}:
        category, score = 'chemistry', 84
    elif planet == 'Jupiter' and house in {1, 4, 7}:
        category, score = 'long_term', 80
    elif planet == 'Saturn' and house in {8, 12}:
        category, score = 'pressure_points', 80
    elif planet in {'Mars', 'Rahu'} and house in {7, 8}:
        category, score = 'chemistry', 77
    elif house in {8, 12}:
        category, score = 'pressure_points', 70
    elif house in {1, 4, 7}:
        category, score = 'long_term', 68
    else:
        category, score = 'chemistry', 64
    return _make_signal(
        f"overlay-{item['source']}-{item['planet']}-{item['target']}-{item['reference']}-h{house}",
        category,
        score,
        f"{item['source']} {item['planet']} -> {item['target']} {item['reference']} H{house}",
        item['note'],
    )


def _dedupe_signals(signals: list[dict]) -> list[dict]:
    deduped = {}
    for signal in signals:
        current = deduped.get(signal['key'])
        if current is None or signal['score'] > current['score']:
            deduped[signal['key']] = signal
    return list(deduped.values())


def _build_final_synthesis(signals: list[dict]) -> dict:
    emotional = _top_signals(signals, 'emotional_fit')
    chemistry = _top_signals(signals, 'chemistry')
    long_term = _top_signals(signals, 'long_term')
    pressure = _top_signals(signals, 'pressure_points')

    def level(items, high=82, mid=70):
        top = items[0]['score'] if items else 0
        if top >= high:
            return 'strong'
        if top >= mid:
            return 'moderate'
        if top > 0:
            return 'mixed'
        return 'unclear'

    return {
        'attraction': level(chemistry),
        'emotional_softness': level(emotional),
        'long_term_stability': level(long_term),
        'karmic_pressure': 'high' if (pressure and pressure[0]['score'] >= 80) else 'moderate' if pressure else 'low',
        'text': (
            f"Attraction is {level(chemistry)}, emotional softness is {level(emotional)}, "
            f"long-term stability is {level(long_term)}, and karmic/pressure factors are "
            f"{'high' if (pressure and pressure[0]['score'] >= 80) else 'moderate' if pressure else 'low'}."
        )
    }


def calculate_synastry(chart_a, chart_b) -> dict:
    """Build a first strong Vedic synastry layer."""
    overlays = _overlay_bundle(chart_a, chart_b, chart_a.name, chart_b.name)
    overlays += _overlay_bundle(chart_b, chart_a, chart_b.name, chart_a.name)
    aspects = _cross_aspects(chart_a, chart_b) + _cross_aspects(chart_b, chart_a)
    conjunctions = _cross_conjunctions(chart_a, chart_b)
    manglik_a = _manglik_report(chart_a)
    manglik_b = _manglik_report(chart_b)
    natal_a = calculate_natal_relationship_capacity(chart_a)
    natal_b = calculate_natal_relationship_capacity(chart_b)
    partnership_axis = _partnership_axis_notes(chart_a, chart_b, chart_a.name, chart_b.name)
    seventh_axis_signals = _build_seventh_axis_analysis(chart_a, chart_b, chart_a.name, chart_b.name)
    d9_module = _build_d9_compatibility(chart_a, chart_b, chart_a.name, chart_b.name)

    signals = [_categorize_overlay_signal(item) for item in overlays]
    for item in conjunctions:
        category = 'chemistry' if any(p in {item['planet_1'], item['planet_2']} for p in ['Venus', 'Mars', 'Rahu']) else 'emotional_fit' if 'Moon' in {item['planet_1'], item['planet_2']} else 'long_term'
        signals.append(_make_signal(
            f"conj-{item['planet_1']}-{item['planet_2']}-{item['sign']}", category, 76,
            f"{item['planet_1']} + {item['planet_2']} conjunction",
            item['note'],
        ))
    for item in aspects:
        category = 'pressure_points' if item['from'] in {'Saturn', 'Mars', 'Rahu', 'Ketu'} else 'long_term' if item['from'] == 'Jupiter' else 'emotional_fit'
        signals.append(_make_signal(
            f"aspect-{item['from']}-{item['to']}-{item['distance']}", category, 68,
            f"{item['from']} aspects {item['to']}",
            item['note'],
        ))
    signals.extend(seventh_axis_signals)
    signals.extend(d9_module['signals'])
    if manglik_a['severity'] != 'none' or manglik_b['severity'] != 'none':
        signals.append(_make_signal(
            'manglik-interaction', 'pressure_points', 74,
            'Manglik interaction',
            f"Manglik interaction: {chart_a.name} is {manglik_a['severity']} and {chart_b.name} is {manglik_b['severity']}. Similar Mars signatures can normalize heat, while mismatched intensity can create conflict style differences.",
        ))

    signals = _dedupe_signals(signals)
    summary = {
        'emotional_fit': _top_signals(signals, 'emotional_fit'),
        'chemistry': _top_signals(signals, 'chemistry'),
        'long_term': _top_signals(signals, 'long_term'),
        'pressure_points': _top_signals(signals, 'pressure_points'),
    }
    final_synthesis = _build_final_synthesis(signals)

    return {
        'natal_capacity': {
            'person_1': natal_a,
            'person_2': natal_b,
        },
        'overlays': overlays,
        'cross_aspects': aspects,
        'cross_conjunctions': conjunctions,
        'manglik': {
            'person_1': manglik_a,
            'person_2': manglik_b,
            'compatibility_note': 'Manglik is treated here as heat/intensity style, not as an automatic relationship failure.',
        },
        'partnership_axis': partnership_axis,
        'seventh_axis': _top_signals(seventh_axis_signals, 'long_term', 3) + _top_signals(seventh_axis_signals, 'pressure_points', 3) + _top_signals(seventh_axis_signals, 'chemistry', 3) + _top_signals(seventh_axis_signals, 'emotional_fit', 3),
        'd9_module': d9_module,
        'summary': summary,
        'final_synthesis': final_synthesis,
        'technical_details': _sort_signals(signals),
    }
