"""Transit (Gochar) calculation engine."""

from datetime import date, timedelta
from dataclasses import dataclass
import swisseph as swe
from .ephemeris import PLANET_IDS, RASHIS, NAKSHATRAS, NAK_SPAN, deg_to_dms

HOUSE_TOPICS = {
    1: 'identity, body, and self-direction',
    2: 'money, speech, and family resources',
    3: 'skills, courage, writing, and initiative',
    4: 'home, roots, private life, and emotional security',
    5: 'creativity, romance, children, and intelligence',
    6: 'work, service, health, and conflict',
    7: 'partnerships, clients, and public dealings',
    8: 'transformation, crisis, secrecy, and depth',
    9: 'belief, teachers, travel, and higher meaning',
    10: 'career, reputation, duty, and visibility',
    11: 'gains, networks, allies, and long-term goals',
    12: 'retreat, loss, sleep, foreignness, and liberation',
}

PLANET_TRANSIT_FOCUS = {
    'Sun': 'purpose, confidence, authority, and visibility',
    'Moon': 'emotional weather, habits, and daily mood',
    'Mars': 'drive, stress, courage, and conflict response',
    'Mercury': 'thinking, conversation, writing, and decisions',
    'Jupiter': 'growth, faith, opportunity, and guidance',
    'Venus': 'relationships, pleasure, beauty, and harmony',
    'Saturn': 'pressure, discipline, duty, and karmic testing',
    'Rahu': 'desire, amplification, ambition, and restlessness',
    'Ketu': 'detachment, release, pruning, and inner distance',
}


@dataclass
class TransitPosition:
    name: str
    longitude: float
    rashi: str
    degree_in_sign: float
    house: int  # from natal Ascendant
    natal_longitude: float
    orb: float  # degrees from natal position


def calculate_transits(chart_data, target_date: date = None) -> dict:
    """Calculate current transit positions relative to a natal chart.

    Args:
        chart_data: ChartData object with natal positions
        target_date: Date to calculate transits for (default: today)

    Returns:
        dict of {planet_name: TransitPosition}
    """
    if target_date is None:
        target_date = date.today()

    swe.set_sid_mode(swe.SIDM_LAHIRI)
    jd = swe.julday(target_date.year, target_date.month, target_date.day, 12)

    asc_rashi = chart_data.ascendant.rashi_index
    transits = {}

    for name, pid in PLANET_IDS.items():
        xx, _ = swe.calc_ut(jd, pid, swe.FLG_SIDEREAL)
        lon = xx[0] % 360
        rashi_idx = int(lon / 30)
        natal_lon = chart_data.planets[name].longitude
        orb = lon - natal_lon
        if orb > 180: orb -= 360
        if orb < -180: orb += 360

        transits[name] = TransitPosition(
            name=name,
            longitude=lon,
            rashi=RASHIS[rashi_idx],
            degree_in_sign=lon % 30,
            house=((rashi_idx - asc_rashi) % 12) + 1,
            natal_longitude=natal_lon,
            orb=orb
        )

    # Nodes
    xx, _ = swe.calc_ut(jd, swe.TRUE_NODE, swe.FLG_SIDEREAL)
    for i, nname in enumerate(['Rahu', 'Ketu']):
        lon = xx[0] % 360 if nname == 'Rahu' else (xx[0] + 180) % 360
        rashi_idx = int(lon / 30)
        natal_lon = chart_data.planets[nname].longitude
        orb = lon - natal_lon
        if orb > 180: orb -= 360
        if orb < -180: orb += 360

        transits[nname] = TransitPosition(
            name=nname,
            longitude=lon,
            rashi=RASHIS[rashi_idx],
            degree_in_sign=lon % 30,
            house=((rashi_idx - asc_rashi) % 12) + 1,
            natal_longitude=natal_lon,
            orb=orb
        )

    return transits


def find_sign_changes(year: int, planet_name: str) -> list[dict]:
    """Find all sign changes for a planet in a given year.

    Args:
        year: Calendar year
        planet_name: Name of the planet

    Returns:
        List of dicts with 'date', 'from_sign', 'to_sign'
    """
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    pid = PLANET_IDS.get(planet_name)
    if pid is None:
        return []

    changes = []
    prev_sign = None

    for day_offset in range(366):
        d = date(year, 1, 1) + timedelta(days=day_offset)
        if d.year != year:
            break
        jd = swe.julday(d.year, d.month, d.day, 12)
        xx, _ = swe.calc_ut(jd, pid, swe.FLG_SIDEREAL)
        sign = RASHIS[int(xx[0] % 360 / 30)]
        if prev_sign and sign != prev_sign:
            changes.append({
                'date': d.isoformat(),
                'from_sign': prev_sign,
                'to_sign': sign
            })
        prev_sign = sign

    return changes


def transit_to_dict(tp: TransitPosition) -> dict:
    """Serialize a TransitPosition to a dict."""
    return {
        'name': tp.name,
        'longitude': round(tp.longitude, 4),
        'rashi': tp.rashi,
        'degree_in_sign': round(tp.degree_in_sign, 4),
        'degree_formatted': deg_to_dms(tp.degree_in_sign),
        'house': tp.house,
        'natal_longitude': round(tp.natal_longitude, 4),
        'orb': round(tp.orb, 2),
    }


def build_transit_reading(chart_data, transits: dict) -> list[dict]:
    """Create beginner-friendly transit readings using natal context."""
    results = []
    focus_order = ['Saturn', 'Jupiter', 'Rahu', 'Ketu', 'Mars', 'Sun', 'Venus', 'Mercury', 'Moon']
    for name in focus_order:
        tp = transits.get(name)
        natal = chart_data.planets.get(name)
        if not tp or not natal:
            continue

        transit_house_topic = HOUSE_TOPICS[tp.house]
        natal_house_topic = HOUSE_TOPICS[natal.house]
        summary = (
            f'Transit {name} is now in {tp.rashi}, moving through H{tp.house} of your chart. '
            f'Your natal {name} is in {natal.rashi} in H{natal.house}, so this transit activates {PLANET_TRANSIT_FOCUS[name]} '
            f'by bringing current movement into {transit_house_topic}, while your natal baseline for that planet begins in {natal_house_topic}.'
        )
        practical = (
            f'In plain English: when natal {name} starts from H{natal.house} but transit {name} passes through H{tp.house}, '
            f'you feel that planet through both layers at once - the birth promise from H{natal.house} and the current trigger through H{tp.house}. '
            f'That is why {name} transits are read as activation, not replacement.'
        )
        results.append({
            'planet': name,
            'summary': summary,
            'practical': practical,
            'transit_house': tp.house,
            'natal_house': natal.house,
            'transit_sign': tp.rashi,
            'natal_sign': natal.rashi,
        })
    return results
