"""Shadbala — 6-fold planetary strength calculation.

Simplified version based on:
1. Sthana Bala (positional strength) — dignity, exaltation, etc.
2. Dig Bala (directional strength) — placement in angular houses
3. Kaala Bala (temporal strength) — day/night, etc.
4. Chesta Bala (motional strength) — direct/retrograde
5. Naisargika Bala (natural strength) — inherent planet strength
6. Drik Bala (aspectual strength) — aspects received

All values in Rupas (1 Rupa = 1 unit of strength).
"""

from .ephemeris import PlanetPosition

# Exaltation signs (0-indexed)
EXALTATION = {
    'Sun': 0, 'Moon': 1, 'Mars': 9, 'Mercury': 5,
    'Jupiter': 3, 'Venus': 11, 'Saturn': 6
}

# Debilitation signs (7th from exaltation)
DEBILITATION = {
    'Sun': 6, 'Moon': 7, 'Mars': 3, 'Mercury': 11,
    'Jupiter': 5, 'Venus': 8, 'Saturn': 0
}

# Own signs
OWN_SIGNS = {
    'Sun': [4], 'Moon': [3], 'Mars': [0, 7], 'Mercury': [2, 5],
    'Jupiter': [8, 11], 'Venus': [1, 6], 'Saturn': [9, 10]
}

# Moolatrikona signs
MOOLATRIKONA = {
    'Sun': [4], 'Moon': [1], 'Mars': [0], 'Mercury': [5],
    'Jupiter': [8], 'Venus': [5], 'Saturn': [10]
}

# Natural strength (Naisargika Bala in Rupas)
NAISARGIKA = {
    'Saturn': 0.5, 'Mars': 0.6, 'Mercury': 0.7, 'Jupiter': 0.8,
    'Venus': 0.9, 'Moon': 1.0, 'Sun': 1.2
}

# Kendra houses for Dig Bala
DIGBALA_HOUSES = {
    'Sun': 10,      # Strongest in H10
    'Moon': 4,      # Strongest in H4
    'Mars': 10,     # Strongest in H10
    'Mercury': 1,   # Strongest in H1
    'Jupiter': 1,   # Strongest in H1
    'Venus': 4,     # Strongest in H4
    'Saturn': 7,    # Strongest in H7
}


def calculate_sthana_bala(planet: str, rashi_index: int) -> float:
    """Sthana Bala: Positional strength based on dignity.

    Exaltation: 1 Rupa
    Moolatrikona: 0.75 Rupa
    Own sign: 0.5 Rupa
    Great friend: 0.75 Rupa
    Friend: 0.5 Rupa
    Neutral: 0.25 Rupa
    Enemy: 0.125 Rupa
    Debilitation: 0
    """
    if planet not in EXALTATION:
        return 0.25

    if rashi_index == EXALTATION[planet]:
        return 1.0  # Exalted
    elif rashi_index == DEBILITATION[planet]:
        return 0.0  # Debilitated
    elif rashi_index in MOOLATRIKONA.get(planet, []):
        return 0.75
    elif rashi_index in OWN_SIGNS.get(planet, []):
        return 0.5
    else:
        return 0.25  # Neutral (simplified)


def calculate_dig_bala(planet: str, house: int) -> float:
    """Dig Bala: Directional strength.

    Strongest in specific Kendra house.
    Maximum = 1 Rupa, Minimum = 0.
    """
    if planet not in DIGBALA_HOUSES:
        return 0.5

    best_house = DIGBALA_HOUSES[planet]
    distance = abs(house - best_house)
    if distance > 6:
        distance = 12 - distance

    # Linear interpolation: 0° = 1.0, 180° = 0
    return max(0, 1.0 - (distance / 6.0))


def calculate_kaala_bala(planet: str, birth_hour: int) -> float:
    """Kaala Bala: Temporal strength (simplified).

    Sun/Mars/Jupiter stronger during day (6-18)
    Moon/Venus/Saturn stronger during night (18-6)
    Mercury is always strong.
    """
    is_daytime = 6 <= birth_hour < 18

    day_planets = {'Sun', 'Mars', 'Jupiter'}
    night_planets = {'Moon', 'Venus', 'Saturn'}

    if planet == 'Mercury':
        return 0.75  # Always strong
    elif planet in day_planets:
        return 0.75 if is_daytime else 0.25
    elif planet in night_planets:
        return 0.75 if not is_daytime else 0.25
    return 0.5


def calculate_chesta_bala(planet: str, is_retrograde: bool) -> float:
    """Chesta Bala: Motional strength.

    Retrograde planets are stronger (1 Rupa).
    Direct planets are moderate (0.5 Rupa).
    Sun and Moon are never retrograde — always strong.
    """
    if planet in ('Sun', 'Moon'):
        return 1.0  # Always have Chesta Bala (they don't retrograde)
    elif is_retrograde:
        return 1.0
    else:
        return 0.5


def calculate_drik_bala(planet: str, aspects_received: list) -> float:
    """Drik Bala: Aspectual strength (simplified).

    Benefic aspects (Jupiter, Venus) add strength.
    Malefic aspects (Saturn, Mars) subtract strength.
    """
    score = 0.5  # Neutral base

    for aspect_from in aspects_received:
        if aspect_from in ('Jupiter', 'Venus'):
            score += 0.15
        elif aspect_from in ('Saturn', 'Mars'):
            score -= 0.1
        elif aspect_from == 'Mercury':
            score += 0.05

    return max(0, min(1.0, score))


def calculate_shadbala(planets: dict[str, PlanetPosition],
                       house_aspects: dict[str, list[str]] = None,
                       birth_hour: int = 12) -> dict:
    """Calculate Shadbala (6-fold strength) for all planets.

    Args:
        planets: dict of {name: PlanetPosition}
        house_aspects: dict of {planet_name: [list of planets aspecting it]}
        birth_hour: hour of birth (0-23)

    Returns:
        dict with per-planet strength breakdown and total scores
    """
    if house_aspects is None:
        house_aspects = {}

    results = {}
    scores = {}

    for name in ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']:
        if name not in planets:
            continue

        p = planets[name]
        aspects_rec = house_aspects.get(name, [])

        sthana = calculate_sthana_bala(name, p.rashi_index)
        dig = calculate_dig_bala(name, p.house)
        kaala = calculate_kaala_bala(name, birth_hour)
        chesta = calculate_chesta_bala(name, p.retrograde)
        naisargika = NAISARGIKA.get(name, 0.5)
        drik = calculate_drik_bala(name, aspects_rec)

        total = sthana + dig + kaala + chesta + naisargika + drik

        results[name] = {
            'sthana_bala': round(sthana, 3),
            'dig_bala': round(dig, 3),
            'kaala_bala': round(kaala, 3),
            'chesta_bala': round(chesta, 3),
            'naisargika_bala': round(naisargika, 3),
            'drik_bala': round(drik, 3),
            'total': round(total, 3),
            'rashi': p.rashi,
            'house': p.house,
            'retrograde': p.retrograde,
            'dignity': _get_dignity(name, p.rashi_index),
        }
        scores[name] = total

    # Rank planets by total strength
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    return {
        'planets': results,
        'ranking': [{'planet': name, 'score': round(score, 3), 'rank': i+1}
                    for i, (name, score) in enumerate(ranked)],
    }


def _get_dignity(planet: str, rashi_index: int) -> str:
    """Get dignity status of a planet."""
    if planet not in EXALTATION:
        return 'neutral'

    if rashi_index == EXALTATION[planet]:
        return 'exalted'
    elif rashi_index == DEBILITATION[planet]:
        return 'debilitated'
    elif rashi_index in MOOLATRIKONA.get(planet, []):
        return 'moolatrikona'
    elif rashi_index in OWN_SIGNS.get(planet, []):
        return 'own_sign'
    else:
        return 'neutral'


def shadbala_to_dict(result: dict) -> dict:
    """Serialize Shadbala result."""
    return result
