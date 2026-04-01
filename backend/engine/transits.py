"""Transit (Gochar) calculation engine."""

from datetime import date, timedelta
from dataclasses import dataclass
import swisseph as swe
from .ephemeris import PLANET_IDS, RASHIS, NAKSHATRAS, NAK_SPAN, deg_to_dms


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
