"""Dosha detection — Mangal, Kaal Sarpa, Sade Sati, Kantaka Shani."""

from dataclasses import dataclass
from .ephemeris import PlanetPosition

DUSTHANA = {6, 8, 12}
KENDRA = {1, 4, 7, 10}


@dataclass
class Dosha:
    name: str
    active: bool
    severity: str  # 'high', 'medium', 'low'
    description: str
    remedy: str


def detect_mangal_dosha(planets: dict[str, PlanetPosition]) -> Dosha:
    """Mangal Dosha (Kuja Dosha): Mars in 1, 2, 4, 7, 8, or 12 from Ascendant.

    Causes delay/conflict in marriage. Cancelled if Mars is in own sign or exalted.
    """
    if 'Mars' not in planets:
        return Dosha('Mangal Dosha', False, 'low', '', '')

    mars = planets['Mars']
    mangal_houses = {1, 2, 4, 7, 8, 12}

    if mars.house in mangal_houses:
        # Check cancellation: Mars in own sign (Aries=0, Scorpio=7) or exalted (Capricorn=9)
        own_or_exalted = mars.rashi_index in (0, 7, 9)
        if own_or_exalted:
            return Dosha(
                'Mangal Dosha',
                True,
                'low',
                f'Mars in H{mars.house} ({mars.rashi}) — present but cancelled by {mars.rashi} placement',
                'Mangal Dosha exists but is significantly weakened. Chant Hanuman Chalisa on Tuesdays.'
            )
        else:
            return Dosha(
                'Mangal Dosha',
                True,
                'high',
                f'Mars in H{mars.house} ({mars.rashi}) — Mangal Dosha active. Affects marriage, partnerships.',
                'Donate red lentils on Tuesdays. Wear Red Coral. Chant Om Ang Angarakaya Namah.'
            )
    else:
        return Dosha('Mangal Dosha', False, 'low', 'Mars not in Mangal Dosha houses (1,2,4,7,8,12).', '')


def detect_kaal_sarpa(planets: dict[str, PlanetPosition]) -> Dosha:
    """Kaal Sarpa Dosha: All planets hemmed between Rahu and Ketu.

    Means all classical planets (Sun-Saturn) are on one side of the Rahu-Ketu axis.
    """
    if 'Rahu' not in planets or 'Ketu' not in planets:
        return Dosha('Kaal Sarpa Dosha', False, 'low', '', '')

    rahu_sign = planets['Rahu'].rashi_index
    ketu_sign = planets['Ketu'].rashi_index

    classical = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']
    all_between = True

    for name in classical:
        if name not in planets:
            continue
        p_sign = planets[name].rashi_index

        # Check if planet is between Rahu and Ketu (clockwise)
        if rahu_sign < ketu_sign:
            if not (rahu_sign < p_sign < ketu_sign):
                all_between = False
                break
        else:  # Wraps around
            if not (p_sign > rahu_sign or p_sign < ketu_sign):
                all_between = False
                break

    if all_between:
        return Dosha(
            'Kaal Sarpa Dosha',
            True,
            'high',
            'All planets hemmed between Rahu-Ketu axis. Creates obstacles, delays, and anxiety.',
            'Worship Lord Shiva. Chant Mahamrityunjaya Mantra. Visit Trimbakeshwar or Kalahasti temple.'
        )
    else:
        return Dosha('Kaal Sarpa Dosha', False, 'low', 'Not all planets are between Rahu-Ketu axis.', '')


def detect_sade_sati(planets: dict[str, PlanetPosition],
                     transit_saturn_sign: int = None) -> Dosha:
    """Sade Sati: Saturn transiting over natal Moon sign.

    Saturn spends ~2.5 years in each sign. Sade Sati = Saturn in Moon sign,
    or 12th/2nd from Moon sign (7.5 year period total).

    Args:
        planets: natal planet positions
        transit_saturn_sign: Saturn's current transit sign index (0-11)
    """
    if 'Moon' not in planets or transit_saturn_sign is None:
        return Dosha('Sade Sati', False, 'low', '', '')

    moon_sign = planets['Moon'].rashi_index

    # Saturn in Moon sign, 12th from Moon, or 2nd from Moon
    sat_from_moon = (transit_saturn_sign - moon_sign) % 12

    if sat_from_moon == 0:
        phase = 'peak (Moon sign)'
        severity = 'high'
        desc = 'Saturn transiting natal Moon sign — peak Sade Sati. Maximum pressure on mind and emotions.'
    elif sat_from_moon == 11:
        phase = 'first phase (12th from Moon)'
        severity = 'medium'
        desc = 'Saturn in 12th from Moon — first phase of Sade Sati. Expenses, isolation, foreign connections.'
    elif sat_from_moon == 1:
        phase = 'third phase (2nd from Moon)'
        severity = 'medium'
        desc = 'Saturn in 2nd from Moon — final phase of Sade Sati. Family and finances tested.'
    else:
        return Dosha('Sade Sati', False, 'low', 'Saturn is not in Sade Sati position.', '')

    return Dosha(
        'Sade Sati',
        True,
        severity,
        f'{desc} Phase: {phase}',
        'Chant Om Sham Shanicharaya Namah on Saturdays. Donate black sesame, mustard oil. Feed crows.'
    )


def detect_kantaka_shani(planets: dict[str, PlanetPosition],
                         transit_saturn_sign: int = None) -> Dosha:
    """Kantaka Shani: Saturn transiting 4th, 7th, or 10th from Moon sign.

    Creates major obstacles in the area of life indicated by the house.
    """
    if 'Moon' not in planets or transit_saturn_sign is None:
        return Dosha('Kantaka Shani', False, 'low', '', '')

    moon_sign = planets['Moon'].rashi_index
    sat_from_moon = (transit_saturn_sign - moon_sign) % 12

    kantaka_positions = {3, 6, 9}  # 4th, 7th, 10th from Moon (0-indexed)

    if sat_from_moon in kantaka_positions:
        house_map = {3: '4th (home/mother)', 6: '7th (marriage/partnerships)', 9: '10th (career)'}
        area = house_map.get(sat_from_moon, 'unknown')
        return Dosha(
            'Kantaka Shani',
            True,
            'high',
            f'Saturn transiting {area} from Moon — major obstacles in this area of life.',
            'Same remedies as Sade Sati. Focus discipline on the affected area.'
        )
    else:
        return Dosha('Kantaka Shani', False, 'low', 'Saturn is not in Kantaka Shani position.', '')


def detect_all_doshas(planets: dict[str, PlanetPosition],
                      transit_saturn_sign: int = None) -> list[Dosha]:
    """Detect all doshas."""
    doshas = []
    doshas.append(detect_mangal_dosha(planets))
    doshas.append(detect_kaal_sarpa(planets))
    doshas.append(detect_sade_sati(planets, transit_saturn_sign))
    doshas.append(detect_kantaka_shani(planets, transit_saturn_sign))
    return [d for d in doshas if d.active]


def dosha_to_dict(d: Dosha) -> dict:
    return {
        'name': d.name,
        'active': d.active,
        'severity': d.severity,
        'description': d.description,
        'remedy': d.remedy,
    }
