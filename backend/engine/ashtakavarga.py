"""Ashtakavarga — 8-fold planetary strength point system.

Each planet contributes bindus (points) to each house/sign.
The total score for each house indicates its strength.

Sources:
- SAV (Sarva Ashtakavarga): Total points per house
- Bhinnashtakavarga: Individual planet's contribution per house
"""

# Ashtakavarga rules: for each planet, which signs get bindus
# Based on position relative to the planet's sign
# Rules from BPHS (Brihat Parashara Hora Shastra)

# Sun's Ashtakavarga: bindu rules
# Sun gives bindu to signs that are:
# 2, 4, 7, 8, 9, 10, 11 from Sun's sign
SUN_BINDU_SIGNS = [2, 4, 7, 8, 9, 10, 11]  # house distances from Sun

# Moon: 1, 3, 5, 6, 7, 9, 10
MOON_BINDU_SIGNS = [1, 3, 5, 6, 7, 9, 10]

# Mars: 1, 2, 4, 7, 8, 9, 10
MARS_BINDU_SIGNS = [1, 2, 4, 7, 8, 9, 10]

# Mercury: 1, 3, 5, 6, 7, 8, 9, 11, 12
MERCURY_BINDU_SIGNS = [1, 3, 5, 6, 7, 8, 9, 11, 12]

# Jupiter: 2, 5, 7, 9, 11
JUPITER_BINDU_SIGNS = [2, 5, 7, 9, 11]

# Venus: 1, 2, 3, 4, 5, 7, 9, 11, 12
VENUS_BINDU_SIGNS = [1, 2, 3, 4, 5, 7, 9, 11, 12]

# Saturn: 3, 5, 6, 10, 11, 12
SATURN_BINDU_SIGNS = [3, 5, 6, 10, 11, 12]

# Ascendant: 1, 2, 4, 7, 8, 9, 10, 11
ASC_BINDU_SIGNS = [1, 2, 4, 7, 8, 9, 10, 11]

PLANET_BINDU_RULES = {
    'Sun': SUN_BINDU_SIGNS,
    'Moon': MOON_BINDU_SIGNS,
    'Mars': MARS_BINDU_SIGNS,
    'Mercury': MERCURY_BINDU_SIGNS,
    'Jupiter': JUPITER_BINDU_SIGNS,
    'Venus': VENUS_BINDU_SIGNS,
    'Saturn': SATURN_BINDU_SIGNS,
}


def calculate_bhinna_ashtakavarga(planet_sign_index: int, planet_name: str) -> list[int]:
    """Calculate Bhinnashtakavarga for one planet.

    Returns a list of 12 values (0 or 1) for each sign,
    indicating whether that sign gets a bindu from this planet's position.

    Args:
        planet_sign_index: 0-11, the sign the planet is in
        planet_name: name of the planet

    Returns:
        list of 12 ints (0 or 1)
    """
    bindu_rules = PLANET_BINDU_RULES.get(planet_name, [])
    result = [0] * 12

    for sign_offset in bindu_rules:
        sign = (planet_sign_index + sign_offset - 1) % 12
        result[sign] = 1

    return result


def calculate_ascendant_bindus(asc_sign_index: int) -> list[int]:
    """Calculate Ascendant's contribution to Ashtakavarga."""
    result = [0] * 12
    for sign_offset in ASC_BINDU_SIGNS:
        sign = (asc_sign_index + sign_offset - 1) % 12
        result[sign] = 1
    return result


def calculate_sarva_ashtakavarga(planets: dict, asc_sign_index: int) -> dict:
    """Calculate full Sarva Ashtakavarga (SAV).

    Args:
        planets: dict of {name: PlanetPosition} with .rashi_index attribute
        asc_sign_index: Ascendant's rashi index (0-11)

    Returns:
        dict with:
        - 'bhinna': {planet_name: [12 bindus]}
        - 'sav': [12 total bindus per sign]
        - 'house_scores': {house_num: total_bindus}
    """
    bhinna = {}
    sav = [0] * 12

    # Calculate for each planet
    for name in ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']:
        if name in planets:
            sign_idx = planets[name].rashi_index
            bindus = calculate_bhinna_ashtakavarga(sign_idx, name)
            bhinna[name] = bindus
            for i in range(12):
                sav[i] += bindus[i]

    # Add Ascendant contribution
    asc_bindus = calculate_ascendant_bindus(asc_sign_index)
    bhinna['Ascendant'] = asc_bindus
    for i in range(12):
        sav[i] += asc_bindus[i]

    # Convert to house scores (sign → house mapping via Ascendant)
    house_scores = {}
    for house in range(1, 13):
        sign = (asc_sign_index + house - 1) % 12
        house_scores[house] = sav[sign]

    return {
        'bhinna': bhinna,
        'sav': sav,
        'house_scores': house_scores,
    }


def interpret_sav_score(score: int, house: int) -> str:
    """Interpret a SAV score for a house."""
    if score >= 30:
        return 'Very strong — excellent results'
    elif score >= 28:
        return 'Strong — good results'
    elif score >= 25:
        return 'Average — moderate results'
    elif score >= 22:
        return 'Weak — challenges in this area'
    else:
        return 'Very weak — significant difficulties'


def ashtakavarga_to_dict(result: dict) -> dict:
    """Serialize Ashtakavarga result."""
    return {
        'bhinna': result['bhinna'],
        'sav': result['sav'],
        'house_scores': result['house_scores'],
    }
