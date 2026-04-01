"""Swiss Ephemeris wrapper for Vedic astrology calculations."""

import swisseph as swe
from dataclasses import dataclass, field
from typing import Optional

# Constants
RASHIS = [
    'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
    'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
]

NAKSHATRAS = [
    'Ashwini', 'Bharani', 'Krittika', 'Rohini', 'Mrigashira', 'Ardra',
    'Punarvasu', 'Pushya', 'Ashlesha', 'Magha', 'P.Phalguni', 'U.Phalguni',
    'Hasta', 'Chitra', 'Swati', 'Vishakha', 'Anuradha', 'Jyeshtha',
    'Mula', 'P.Ashadha', 'U.Ashadha', 'Sravana', 'Dhanishtha', 'Shatabhisha',
    'P.Bhadrapada', 'U.Bhadrapada', 'Revati'
]

NAKSHATRA_LORDS = [
    'Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu',       # Ashwini-Ardra
    'Jupiter', 'Saturn', 'Mercury',                          # Punarvasu-Ashlesha
    'Ketu', 'Venus', 'Sun',                                  # Magha-U.Phalguni
    'Moon', 'Mars', 'Rahu',                                  # Hasta-Swati
    'Jupiter', 'Saturn', 'Mercury',                          # Vishakha-Jyeshtha
    'Ketu', 'Venus', 'Sun',                                  # Mula-U.Ashadha
    'Moon', 'Mars', 'Rahu',                                  # Sravana-Shatabhisha
    'Jupiter', 'Saturn', 'Mercury'                           # P.Bhadrapada-Revati
]

RASHI_LORDS = [
    'Mars', 'Venus', 'Mercury', 'Moon', 'Sun', 'Mercury',
    'Venus', 'Mars', 'Jupiter', 'Saturn', 'Saturn', 'Jupiter'
]

NAK_SPAN = 360.0 / 27  # 13.333... degrees per nakshatra

PLANET_IDS = {
    'Sun': swe.SUN,
    'Moon': swe.MOON,
    'Mars': swe.MARS,
    'Mercury': swe.MERCURY,
    'Jupiter': swe.JUPITER,
    'Venus': swe.VENUS,
    'Saturn': swe.SATURN,
}

PLANET_NAMES = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu']


@dataclass
class PlanetPosition:
    name: str
    longitude: float
    rashi: str = ''
    rashi_index: int = 0
    nakshatra: str = ''
    nakshatra_index: int = 0
    pada: int = 0
    house: int = 0
    retrograde: bool = False
    degree_in_sign: float = 0.0

    def __post_init__(self):
        self.rashi_index = int(self.longitude % 360 / 30)
        self.rashi = RASHIS[self.rashi_index]
        self.degree_in_sign = self.longitude % 360 % 30
        self.nakshatra_index = int((self.longitude % 360) / NAK_SPAN)
        self.nakshatra = NAKSHATRAS[self.nakshatra_index]
        remainder = (self.longitude % 360) - (self.nakshatra_index * NAK_SPAN)
        self.pada = min(int(remainder / (NAK_SPAN / 4)) + 1, 4)


@dataclass
class ChartData:
    name: str
    birth_date: str  # YYYY-MM-DD
    birth_time: str  # HH:MM
    birth_place: str
    latitude: float
    longitude: float
    ayanamsa: float = 0.0
    ascendant: Optional[PlanetPosition] = None
    planets: dict = field(default_factory=dict)
    house_cusps_whole: list = field(default_factory=list)
    house_cusps_placidus: list = field(default_factory=list)


def get_julian_day(year: int, month: int, day: int, hour: int, minute: int,
                   tz_offset: float = -3.0) -> float:
    """Convert birth data to Julian Day (UTC).

    tz_offset: hours ahead of UTC. E.g., São Paulo = -3, India = +5.5
    UTC = local time - tz_offset  (e.g., 15:55 - (-3) = 18:55 UTC)
    """
    utc_hour = hour - tz_offset + minute / 60.0
    return swe.julday(year, month, day, utc_hour)


def calculate_planet(jd: float, planet_id: int, name: str) -> PlanetPosition:
    """Calculate a single planet's sidereal position."""
    xx, ret = swe.calc_ut(jd, planet_id, swe.FLG_SIDEREAL)
    lon = xx[0] % 360
    # Check retrograde (speed < 0)
    xx_speed, _ = swe.calc_ut(jd, planet_id, swe.FLG_SIDEREAL | swe.FLG_SPEED)
    retro = xx_speed[3] < 0
    return PlanetPosition(name=name, longitude=lon, retrograde=retro)


def calculate_nodes(jd: float) -> tuple[PlanetPosition, PlanetPosition]:
    """Calculate Rahu and Ketu (True Node)."""
    xx, _ = swe.calc_ut(jd, swe.TRUE_NODE, swe.FLG_SIDEREAL)
    rahu_lon = xx[0] % 360
    ketu_lon = (rahu_lon + 180) % 360
    return (
        PlanetPosition(name='Rahu', longitude=rahu_lon),
        PlanetPosition(name='Ketu', longitude=ketu_lon)
    )


def calculate_ascendant(jd: float, lat: float, lon: float) -> PlanetPosition:
    """Calculate sidereal Ascendant (Whole Sign)."""
    _, ascmc = swe.houses_ex(jd, lat, lon, b'W', swe.FLG_SIDEREAL)
    asc_lon = ascmc[0] % 360
    return PlanetPosition(name='Ascendant', longitude=asc_lon)


def calculate_chart(year: int, month: int, day: int, hour: int, minute: int,
                    lat: float, lon: float, name: str = '',
                    place: str = '', tz_offset: float = -3.0) -> ChartData:
    """Calculate a complete Vedic chart."""

    # Set Lahiri ayanamsa
    swe.set_sid_mode(swe.SIDM_LAHIRI)

    jd = get_julian_day(year, month, day, hour, minute, tz_offset)
    ayanamsa = swe.get_ayanamsa(jd)

    # Calculate all planets
    planets = {}
    for pname, pid in PLANET_IDS.items():
        planets[pname] = calculate_planet(jd, pid, pname)

    # Calculate nodes
    rahu, ketu = calculate_nodes(jd)
    planets['Rahu'] = rahu
    planets['Ketu'] = ketu

    # Calculate ascendant
    asc = calculate_ascendant(jd, lat, lon)

    # Assign houses (Whole Sign from Ascendant)
    asc_rashi = asc.rashi_index
    for p in planets.values():
        p.house = ((p.rashi_index - asc_rashi) % 12) + 1

    # House cusps
    cusps_whole, ascmc = swe.houses_ex(jd, lat, lon, b'W', swe.FLG_SIDEREAL)
    cusps_plac, _ = swe.houses_ex(jd, lat, lon, b'P', swe.FLG_SIDEREAL)

    chart = ChartData(
        name=name,
        birth_date=f'{year:04d}-{month:02d}-{day:02d}',
        birth_time=f'{hour:02d}:{minute:02d}',
        birth_place=place,
        latitude=lat,
        longitude=lon,
        ayanamsa=ayanamsa,
        ascendant=asc,
        planets=planets,
        house_cusps_whole=[c % 360 for c in cusps_whole],
        house_cusps_placidus=[c % 360 for c in cusps_plac],
    )

    return chart


def deg_to_dms(deg: float) -> str:
    """Convert decimal degrees to D°M'S\" format."""
    deg = deg % 360
    d = int(deg)
    m = int((deg - d) * 60)
    s = ((deg - d) * 60 - m) * 60
    return f"{d}°{m:02d}'{s:04.1f}\""


def get_rashi_lord(rashi_index: int) -> str:
    """Get the lord of a rashi."""
    return RASHI_LORDS[rashi_index]


def get_nakshatra_lord(nakshatra_index: int) -> str:
    """Get the lord of a nakshatra."""
    return NAKSHATRA_LORDS[nakshatra_index]
