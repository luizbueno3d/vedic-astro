"""KP (Krishnamurti Paddhati) Bhava Chalit system.

KP Bhava Chalit uses unequal house cusps, but the sign-based house mapping used
by this app is derived from the midpoint between adjacent cusps. That midpoint
can shift the effective ascendant sign away from the raw D1 ascendant sign.
"""

from dataclasses import dataclass
from .ephemeris import PlanetPosition, ChartData, RASHIS, NAK_SPAN

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


def _normalize_angle(angle: float) -> float:
    return angle % 360.0


def _forward_midpoint(start: float, end: float) -> float:
    """Return the midpoint when moving forward from start to end."""
    span = (_normalize_angle(end) - _normalize_angle(start)) % 360.0
    return _normalize_angle(start + span / 2.0)


def _get_kp_house_midpoint(chart: ChartData, house_number: int) -> float:
    """Return the midpoint between a house cusp and the next cusp."""
    cusps = chart.house_cusps_placidus
    if len(cusps) != 12:
        raise ValueError('KP house calculation requires 12 placidus cusps')

    idx = house_number - 1
    return _forward_midpoint(cusps[idx], cusps[(idx + 1) % 12])


def get_kp_ascendant_index(chart: ChartData) -> int:
    """Compute the KP effective ascendant sign from the 1st-house midpoint.

    KP Bhava Chalit cusps come from the unequal house system. For the compact
    sign-based mapping used elsewhere in the app, we take the midpoint between
    the 1st and 2nd cusps and use the sign containing that midpoint as the
    effective ascendant sign.
    """
    midpoint = _get_kp_house_midpoint(chart, 1)
    return int(midpoint / 30)


def calculate_kp_house(planet: PlanetPosition, kp_asc_idx: int) -> int:
    """Calculate KP house from the planet's actual natal rashi."""
    return ((planet.rashi_index - kp_asc_idx) % 12) + 1


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
    if asc is None:
        raise ValueError('KP calculation requires a chart ascendant')

    d1_asc_idx = asc.rashi_index
    kp_asc_idx = get_kp_ascendant_index(chart)

    asc_sl = get_sub_lord(asc.nakshatra_index, asc.pada)
    asc_kp_house = ((d1_asc_idx - kp_asc_idx) % 12) + 1

    kp_planets = {}
    planet_houses = {}

    for name, planet in chart.planets.items():
        sl = get_sub_lord(planet.nakshatra_index, planet.pada)
        kp_house = calculate_kp_house(planet, kp_asc_idx)

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
