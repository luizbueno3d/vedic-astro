"""Planetary aspects (Drishti) and conjunction detection."""

from dataclasses import dataclass
from .ephemeris import PlanetPosition, RASHI_LORDS

# Vedic aspect rules: planet → list of house distances it aspects
# All planets aspect 7th. Special aspects for Mars, Jupiter, Saturn.
SPECIAL_ASPECTS = {
    'Mars':    [4, 7, 8],     # +3, +6, +7 houses
    'Jupiter': [5, 7, 9],     # +4, +6, +8 houses
    'Saturn':  [3, 7, 10],    # +2, +6, +9 houses
}

# Standard aspect orbs (in degrees) — generous for conjunction
CONJUNCTION_ORB = 8.0    # Planets within 8° = conjunction
TIGHT_CONJUNCTION_ORB = 3.0  # Within 3° = tight conjunction
ASPECT_ORB = 6.0         # Standard orb for aspects


@dataclass
class Conjunction:
    planet_1: str
    planet_2: str
    house: int
    sign: str
    orb: float
    is_tight: bool


@dataclass
class Aspect:
    from_planet: str
    to_planet: str
    aspect_type: str  # '7th', '4th', '5th', etc.
    from_house: int
    to_house: int
    orb: float
    is_applying: bool  # True if aspect is tightening


def find_conjunctions(planets: dict[str, PlanetPosition]) -> list[Conjunction]:
    """Find all planetary conjunctions (planets in same house within orb).

    Args:
        planets: dict of {name: PlanetPosition}

    Returns:
        List of Conjunction objects
    """
    conjunctions = []
    names = [n for n in planets if n not in ('Rahu', 'Ketu')]
    # Also check nodes separately
    all_names = list(planets.keys())

    for i in range(len(all_names)):
        for j in range(i + 1, len(all_names)):
            p1 = planets[all_names[i]]
            p2 = planets[all_names[j]]

            # Check if same house (Whole Sign)
            if p1.rashi_index == p2.rashi_index:
                orb = abs(p1.longitude - p2.longitude)
                if orb > 180:
                    orb = 360 - orb

                if orb <= CONJUNCTION_ORB:
                    conjunctions.append(Conjunction(
                        planet_1=all_names[i],
                        planet_2=all_names[j],
                        house=p1.house,
                        sign=p1.rashi,
                        orb=round(orb, 2),
                        is_tight=orb <= TIGHT_CONJUNCTION_ORB
                    ))

    return conjunctions


def find_aspects(planets: dict[str, PlanetPosition]) -> list[Aspect]:
    """Find all planetary aspects (Drishti).

    Args:
        planets: dict of {name: PlanetPosition}

    Returns:
        List of Aspect objects
    """
    aspects = []
    planet_names = list(planets.keys())

    for from_name in planet_names:
        from_planet = planets[from_name]
        from_rashi = from_planet.rashi_index

        # Get aspect distances for this planet
        if from_name in ('Rahu', 'Ketu'):
            # Nodes aspect same as Saturn (3, 7, 10) in some traditions
            aspect_distances = [3, 7, 10]
        elif from_name in SPECIAL_ASPECTS:
            aspect_distances = SPECIAL_ASPECTS[from_name] + [7]  # Always include 7th
        else:
            aspect_distances = [7]  # Only 7th aspect for Sun, Moon, Mercury, Venus

        # Remove duplicates
        aspect_distances = list(set(aspect_distances))

        for to_name in planet_names:
            if from_name == to_name:
                continue

            to_planet = planets[to_name]
            to_rashi = to_planet.rashi_index

            # Calculate house distance
            house_distance = (to_rashi - from_rashi) % 12 + 1

            if house_distance in aspect_distances:
                # Calculate orb (how exact the aspect is)
                expected_angle = (house_distance - 1) * 30
                actual_angle = (to_planet.longitude - from_planet.longitude) % 360
                orb = abs(actual_angle - expected_angle)
                if orb > 180:
                    orb = 360 - orb

                # Determine if applying (aspect getting tighter)
                is_applying = orb > 0 and orb < ASPECT_ORB

                # Aspect label
                if house_distance == 7:
                    label = '7th'
                elif from_name == 'Mars' and house_distance == 4:
                    label = '4th (special)'
                elif from_name == 'Mars' and house_distance == 8:
                    label = '8th (special)'
                elif from_name == 'Jupiter' and house_distance == 5:
                    label = '5th (special)'
                elif from_name == 'Jupiter' and house_distance == 9:
                    label = '9th (special)'
                elif from_name == 'Saturn' and house_distance == 3:
                    label = '3rd (special)'
                elif from_name == 'Saturn' and house_distance == 10:
                    label = '10th (special)'
                else:
                    label = f'{house_distance}th'

                aspects.append(Aspect(
                    from_planet=from_name,
                    to_planet=to_name,
                    aspect_type=label,
                    from_house=from_planet.house,
                    to_house=to_planet.house,
                    orb=round(orb, 2),
                    is_applying=is_applying
                ))

    return aspects


def conjunction_to_dict(c: Conjunction) -> dict:
    return {
        'planets': [c.planet_1, c.planet_2],
        'house': c.house,
        'sign': c.sign,
        'orb': c.orb,
        'tight': c.is_tight,
    }


def aspect_to_dict(a: Aspect) -> dict:
    return {
        'from': a.from_planet,
        'to': a.to_planet,
        'type': a.aspect_type,
        'from_house': a.from_house,
        'to_house': a.to_house,
        'orb': a.orb,
        'applying': a.is_applying,
    }
