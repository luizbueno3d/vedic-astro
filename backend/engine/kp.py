"""KP (Krishnamurti Paddhati) Bhava Chalit system — Nakshatra Nadi approach.

In KP, house positions are determined by NAKSHATRA PADA sub-lords,
not by sign-based house boundaries. This gives more precise planetary
significations for Dasha timing.
"""

from dataclasses import dataclass
from typing import Optional
from .ephemeris import (
    PlanetPosition, ChartData, RASHIS, NAKSHATRAS, NAKSHATRA_LORDS,
    NAK_SPAN, get_rashi_lord, RASHI_LORDS
)

SUB_LORD_SEQUENCE = [
    'Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu'
]


def get_nakshatra_pada_index(nakshatra_index: int, pada: int) -> int:
    """Get 0-indexed pada number (0-3) within a nakshatra."""
    return pada - 1


def get_sub_lord(nakshatra_index: int, pada: int) -> str:
    """Get the sub-lord for a nakshatra pada.

    The 108 nakshatra padas are ruled in sequence by the 9 planets:
    Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu, Ketu (repeating).
    """
    pada_0 = pada - 1
    pada_global = nakshatra_index * 4 + pada_0
    sl_idx = pada_global % 9
    return SUB_LORD_SEQUENCE[sl_idx]


def get_sub_lord_from_longitude(longitude: float) -> str:
    """Get sub-lord directly from planetary longitude."""
    nak_idx = int((longitude % 360) / NAK_SPAN)
    remainder = (longitude % 360) - (nak_idx * NAK_SPAN)
    pada = min(int(remainder / (NAK_SPAN / 4)) + 1, 4)
    return get_sub_lord(nak_idx, pada)


@dataclass
class KPPlanetPlacement:
    planet: str
    nakshatra: str
    nakshatra_index: int
    pada: int
    sub_lord: str
    rashi: str
    rashi_index: int
    kp_house: int


@dataclass
class KPBhavaChalit:
    asc_nakshatra: str
    asc_pada: int
    asc_sub_lord: str
    asc_house: int
    planets: dict[str, KPPlanetPlacement]
    house_rulerships: dict[str, list[int]]
    planet_houses: dict[str, int]


def calculate_kp_house(planet_longitude: float, asc_rashi_index: int) -> int:
    """Calculate which house a planet occupies in KP Bhava Chalit.

    The planet's house is determined by which house contains its sub-lord
    in the birth rashi chart.
    """
    sub_lord = get_sub_lord_from_longitude(planet_longitude)
    sl_nak_idx = NAKSHATRAS.index(get_sub_lord_nakshatra(sub_lord))
    sl_rasi = get_sub_lord_rashi(sub_lord)
    sl_rasi_idx = RASHIS.index(sl_rasi)
    kp_house = ((sl_rasi_idx - asc_rashi_index) % 12) + 1
    return kp_house


def get_sub_lord_nakshatra(sub_lord: str) -> str:
    """Find which nakshatra the sub-lord naturally falls in (first occurrence).

    This maps each sub-lord to its natural nakshatra position.
    Sub-lords are distributed across nakshatras as follows:
    - Each nakshatra's 4 padas have sub-lords from the sequence
    - The first occurrence of each sub-lord as a nakshatra lord gives its base
    """
    lord_naksha = {
        'Sun': 'Krittika', 'Moon': 'Rohini', 'Mars': 'Mrigashira',
        'Mercury': 'Ashlesha', 'Jupiter': 'Punarvasu', 'Venus': 'Bharani',
        'Saturn': 'Pushya', 'Rahu': 'Ardra', 'Ketu': 'Mula'
    }
    return lord_naksha.get(sub_lord, 'Ashwini')


def get_sub_lord_rashi(sub_lord: str) -> str:
    """Get the natural rashi placement of a sub-lord planet.

    In the KP system, sub-lords maintain their natural sign relationships:
    - Sun: Aries (exalted), Moon: Cancer (exalted), Mars: Aries (exalted)
    - Mercury: Virgo (exalted), Jupiter: Cancer (exalted), Venus: Taurus (exalted)
    - Saturn: Libra (exalted), Rahu: Taurus, Ketu: Scorpio
    """
    rashi_for = {
        'Sun': 'Aries', 'Moon': 'Cancer', 'Mars': 'Aries',
        'Mercury': 'Virgo', 'Jupiter': 'Cancer', 'Venus': 'Taurus',
        'Saturn': 'Libra', 'Rahu': 'Taurus', 'Ketu': 'Scorpio'
    }
    return rashi_for.get(sub_lord, 'Aries')


def _get_planet_rashi_index(chart: ChartData, planet_name: str) -> int:
    """Get the rashi index of a planet from the chart."""
    if planet_name == 'Ascendant':
        return chart.ascendant.rashi_index
    return chart.planets[planet_name].rashi_index


def calculate_kp_bhava_chalit(chart: ChartData) -> KPBhavaChalit:
    """Calculate full KP Bhava Chalit chart.

    Args:
        chart: Full birth chart from ephemeris

    Returns:
        KPBhavaChalit with planet placements and house assignments
    """
    asc = chart.ascendant
    asc_rashi_idx = asc.rashi_index

    asc_sl = get_sub_lord(asc.nakshatra_index, asc.pada)
    asc_kp_house = calculate_kp_house(asc.longitude, asc_rashi_idx)

    kp_planets = {}
    planet_houses = {}

    for name, planet in chart.planets.items():
        sl = get_sub_lord(planet.nakshatra_index, planet.pada)
        kp_house = calculate_kp_house(planet.longitude, asc_rashi_idx)

        kp_planets[name] = KPPlanetPlacement(
            planet=name,
            nakshatra=planet.nakshatra,
            nakshatra_index=planet.nakshatra_index,
            pada=planet.pada,
            sub_lord=sl,
            rashi=planet.rashi,
            rashi_index=planet.rashi_index,
            kp_house=kp_house,
        )
        planet_houses[name] = kp_house

    house_rulerships: dict[str, list[int]] = {p: [] for p in ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu']}

    for name, placement in kp_planets.items():
        lord = placement.sub_lord
        if lord in house_rulerships:
            house_rulerships[lord].append(placement.kp_house)

    return KPBhavaChalit(
        asc_nakshatra=asc.nakshatra,
        asc_pada=asc.pada,
        asc_sub_lord=asc_sl,
        asc_house=asc_kp_house,
        planets=kp_planets,
        house_rulerships=house_rulerships,
        planet_houses=planet_houses,
    )


def kp_to_dict(kp: KPBhavaChalit) -> dict:
    """Serialize KPBhavaChalit to a dict for JSON output."""
    return {
        'ascendant': {
            'nakshatra': kp.asc_nakshatra,
            'pada': kp.asc_pada,
            'sub_lord': kp.asc_sub_lord,
            'kp_house': kp.asc_house,
        },
        'planets': {
            name: {
                'nakshatra': p.nakshatra,
                'pada': p.pada,
                'sub_lord': p.sub_lord,
                'rashi': p.rashi,
                'kp_house': p.kp_house,
            }
            for name, p in kp.planets.items()
        },
        'house_rulerships': kp.house_rulerships,
        'planet_houses': kp.planet_houses,
    }


def get_kp_dasha_significator(planet_name: str, kp: KPBhavaChalit) -> list[str]:
    """Get the houses a planet significates in KP system.

    In KP, a planet signifies:
    1. The house it occupies
    2. The houses ruled by its sub-lord
    3. The house containing its sub-lord
    """
    significations = [kp.planet_houses.get(planet_name, 0)]

    planet_data = kp.planets.get(planet_name)
    if not planet_data:
        return significations

    sl = planet_data.sub_lord
    sl_rashi_idx = RASHIS.index(get_sub_lord_rashi(sl))
    asc_idx = kp.planets['Ascendant'].kp_house if 'Ascendant' in kp.planets else 0

    for name, p in kp.planets.items():
        if p.sub_lord == sl and name != planet_name:
            significations.append(p.kp_house)

    return list(set(significations))
