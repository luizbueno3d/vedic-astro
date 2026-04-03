"""KP (Krishnamurti Paddhati) Bhava Chalit system.

In KP, house positions differ from Whole Sign because the KP system
uses a different ascendant reference point for Bhava Chalit house calculation.
The sub-lord sequence is used for finer significations, not for the
primary house shift.
"""

from dataclasses import dataclass
from .ephemeris import (
    PlanetPosition, ChartData, RASHIS, NAKSHATRAS, NAKSHATRA_LORDS,
    NAK_SPAN
)

SUB_LORD_SEQUENCE = [
    'Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury'
]


def get_sub_lord(nakshatra_index: int, pada: int) -> str:
    """Get the sub-lord for a nakshatra pada.

    The 108 nakshatra padas are ruled in sequence by the 9 planets
    (KP sub-lord sequence):
    Ketu, Venus, Sun, Moon, Mars, Rahu, Jupiter, Saturn, Mercury (repeating).
    """
    pada_global = nakshatra_index * 4 + (pada - 1)
    return SUB_LORD_SEQUENCE[pada_global % 9]


def get_sub_lord_from_longitude(longitude: float) -> str:
    """Get sub-lord directly from planetary longitude."""
    nak_idx = int((longitude % 360) / NAK_SPAN)
    remainder = (longitude % 360) - (nak_idx * NAK_SPAN)
    pada = min(int(remainder / (NAK_SPAN / 4)) + 1, 4)
    return get_sub_lord(nak_idx, pada)


def get_kp_ascendant_index(chart: ChartData) -> int:
    """Compute the KP effective ascendant sign index.

    When the natal ascendant falls in the LAST pada of its nakshatra
    (pada 4), and is approaching the next sign cusp, KP Bhava Chalit
    uses the NEXT sign as the effective ascendant for house calculations.
    This is the key difference from D1 Whole Sign houses.
    """
    asc = chart.ascendant
    if asc.pada == 4:
        return (asc.rashi_index + 1) % 12
    return asc.rashi_index


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
    d1_asc_rashi: str
    kp_asc_rashi: str
    d1_asc_idx: int
    kp_asc_idx: int
    asc_pada: int
    asc_sub_lord: str
    asc_kp_house: int
    planets: dict[str, KPPlanetPlacement]
    house_rulerships: dict[str, list[int]]
    planet_houses: dict[str, int]


def calculate_kp_bhava_chalit(chart: ChartData) -> KPBhavaChalit:
    """Calculate full KP Bhava Chalit chart.

    The KP house for each planet is determined by:
    1. The planet's sign (rashi_index)
    2. The KP effective ascendant (may differ from D1 ascendant)

    The sub-lord is also computed for each planet for fine KP
    interpretation and Dasha signification work.
    """
    asc = chart.ascendant
    d1_asc_idx = asc.rashi_index
    kp_asc_idx = get_kp_ascendant_index(chart)

    asc_sl = get_sub_lord(asc.nakshatra_index, asc.pada)
    asc_kp_house = ((d1_asc_idx - kp_asc_idx) % 12) + 1

    kp_planets = {}
    planet_houses = {}

    for name, planet in chart.planets.items():
        sl = get_sub_lord(planet.nakshatra_index, planet.pada)
        kp_house = ((planet.rashi_index - kp_asc_idx) % 12) + 1

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

    house_rulerships: dict[str, list[int]] = {
        p: [] for p in ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu']
    }

    for name, placement in kp_planets.items():
        lord = placement.sub_lord
        if lord in house_rulerships:
            house_rulerships[lord].append(placement.kp_house)

    return KPBhavaChalit(
        d1_asc_rashi=RASHIS[d1_asc_idx],
        kp_asc_rashi=RASHIS[kp_asc_idx],
        d1_asc_idx=d1_asc_idx,
        kp_asc_idx=kp_asc_idx,
        asc_pada=asc.pada,
        asc_sub_lord=asc_sl,
        asc_kp_house=asc_kp_house,
        planets=kp_planets,
        house_rulerships=house_rulerships,
        planet_houses=planet_houses,
    )


def kp_to_dict(kp: KPBhavaChalit) -> dict:
    """Serialize KPBhavaChalit to a dict for JSON output."""
    return {
        'd1_asc_rashi': kp.d1_asc_rashi,
        'kp_asc_rashi': kp.kp_asc_rashi,
        'd1_asc_idx': kp.d1_asc_idx,
        'kp_asc_idx': kp.kp_asc_idx,
        'ascendant': {
            'nakshatra': kp.d1_asc_rashi,
            'pada': kp.asc_pada,
            'sub_lord': kp.asc_sub_lord,
            'kp_house': kp.asc_kp_house,
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
