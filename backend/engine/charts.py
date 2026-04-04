"""Divisional chart calculations.

Important: only the core formulas implemented explicitly below should be treated as
verified. Several higher vargas remain simplified and should not be presented as
fully validated until backed by reference checks.
"""

from .ephemeris import PlanetPosition, RASHIS


def get_part(longitude: float, divisions: int) -> tuple[int, int]:
    """Get sign index and 1-indexed part within sign."""
    ri = int(longitude % 360 / 30)
    rem = longitude % 360 % 30
    # Use multiplication to avoid floating point division errors
    part = min(int(rem * divisions / 30.0), divisions - 1) + 1
    return ri, part


def get_part_0(longitude: float, divisions: int) -> tuple[int, int]:
    """Get sign index and 0-indexed part within sign."""
    ri = int(longitude % 360 / 30)
    rem = longitude % 360 % 30
    part = min(int(rem * divisions / 30.0), divisions - 1)
    return ri, part


def _sign_type_offset(rashi_index: int, movable_offset: int, fixed_offset: int, dual_offset: int) -> int:
    """Return offset by sign modality."""
    if rashi_index in {0, 3, 6, 9}:  # movable
        return movable_offset
    if rashi_index in {1, 4, 7, 10}:  # fixed
        return fixed_offset
    return dual_offset


# ===== CORE FORMULAS (checked against reference outputs) =====

def d2_hora(longitude: float) -> str:
    """D2 Hora — Wealth. Verified."""
    ri = int(longitude % 360 / 30)
    rem = longitude % 360 % 30
    part = 0 if rem < 15 else 1
    if ri % 2 == 0:  # Odd sign (0-indexed)
        return 'Leo' if part == 0 else 'Cancer'
    else:  # Even sign
        return 'Cancer' if part == 0 else 'Leo'


def d3_drekkana(longitude: float) -> str:
    """D3 Drekkana — sign, 5th, 9th from the natal sign."""
    ri, p0 = get_part_0(longitude, 3)
    return RASHIS[(ri + p0 * 4) % 12]


def d4_chaturthamsa(longitude: float) -> str:
    """D4 Chaturthamsa — sign, 4th, 7th, 10th from the natal sign."""
    ri, p0 = get_part_0(longitude, 4)
    return RASHIS[(ri + p0 * 3) % 12]


def d7_saptamsha(longitude: float) -> str:
    """D7 Saptamsha — odd signs start from same sign, even signs from the 7th."""
    ri, p0 = get_part_0(longitude, 7)
    start = ri if ri % 2 == 0 else (ri + 6) % 12
    return RASHIS[(start + p0) % 12]


def d9_navamsha(longitude: float) -> str:
    """D9 Navamsha — movable signs start from same sign, fixed from 9th, dual from 5th."""
    ri, p0 = get_part_0(longitude, 9)
    start = (ri + _sign_type_offset(ri, 0, 8, 4)) % 12
    return RASHIS[(start + p0) % 12]


def d10_dashamsha(longitude: float) -> str:
    """D10 Dashamsha — odd signs start from same sign, even signs from the 9th."""
    ri, p0 = get_part_0(longitude, 10)
    start = ri if ri % 2 == 0 else (ri + 8) % 12
    return RASHIS[(start + p0) % 12]


def d12_dwadasamsa(longitude: float) -> str:
    """D12 Dwadasamsa — starts from the natal sign itself."""
    ri, p0 = get_part_0(longitude, 12)
    return RASHIS[(ri + p0) % 12]


def d16_shodasamsa(longitude: float) -> str:
    """D16 Shodasamsa — Vehicles. Formula: (sign + part) % 12 (simplified)."""
    ri, p0 = get_part_0(longitude, 16)
    return RASHIS[(ri + p0) % 12]


def d20_vimsamsa(longitude: float) -> str:
    """D20 Vimsamsa — Spiritual. Formula: (sign + part) % 12 (simplified)."""
    ri, p0 = get_part_0(longitude, 20)
    return RASHIS[(ri + p0) % 12]


def d24_chaturvimsamsa(longitude: float) -> str:
    """D24 Chaturvimsamsa — Education. Formula: (sign + part) % 12 (simplified)."""
    ri, p0 = get_part_0(longitude, 24)
    return RASHIS[(ri + p0) % 12]


def d27_bhamsa(longitude: float) -> str:
    """D27 Bhamsa — Strength. Formula: (sign + part) % 12 (simplified)."""
    ri, p0 = get_part_0(longitude, 27)
    return RASHIS[(ri + p0) % 12]


def d30_trimsamsa(longitude: float) -> str:
    """D30 Trimsamsa — Misfortune. Non-uniform divisions (simplified)."""
    ri, p0 = get_part_0(longitude, 30)
    return RASHIS[(ri + p0) % 12]


def d40_khavedamsa(longitude: float) -> str:
    """D40 Khavedamsa — Maternal lineage. Formula: (sign + part) % 12 (simplified)."""
    ri, p0 = get_part_0(longitude, 40)
    return RASHIS[(ri + p0) % 12]


def d45_akshavedamsa(longitude: float) -> str:
    """D45 Akshavedamsa — Paternal lineage. Formula: (sign + part) % 12 (simplified)."""
    ri, p0 = get_part_0(longitude, 45)
    return RASHIS[(ri + p0) % 12]


def d60_shashtiamsa(longitude: float) -> str:
    """D60 Shashtiamsa — Past life karma. Formula: (sign + part) % 12 (simplified)."""
    ri, p0 = get_part_0(longitude, 60)
    return RASHIS[(ri + p0) % 12]


# ===== VARGA TABLE =====

VARGA_FUNCTIONS = {
    'D2': (d2_hora, 'Hora', 'Wealth'),
    'D3': (d3_drekkana, 'Drekkana', 'Siblings'),
    'D4': (d4_chaturthamsa, 'Chaturthamsa', 'Property'),
    'D7': (d7_saptamsha, 'Saptamamsha', 'Children'),
    'D9': (d9_navamsha, 'Navamsha', 'Marriage'),
    'D10': (d10_dashamsha, 'Dashamamsha', 'Career'),
    'D12': (d12_dwadasamsa, 'Dwadasamsa', 'Parents'),
    'D16': (d16_shodasamsa, 'Shodasamsa', 'Vehicles'),
    'D20': (d20_vimsamsa, 'Vimsamsa', 'Spiritual'),
    'D24': (d24_chaturvimsamsa, 'Chaturvimsamsa', 'Education'),
    'D27': (d27_bhamsa, 'Bhamsa', 'Strength'),
    'D30': (d30_trimsamsa, 'Trimsamsa', 'Misfortune'),
    'D40': (d40_khavedamsa, 'Khavedamsa', 'Maternal lineage'),
    'D45': (d45_akshavedamsa, 'Akshavedamsa', 'Paternal lineage'),
    'D60': (d60_shashtiamsa, 'Shashtiamsa', 'Past life karma'),
}


VARGA_META = {
    'D2': {
        'tier': 'topic',
        'audience': 'advanced',
        'ai_eligible': False,
        'status': 'method-sensitive',
        'plain_english': 'Money style, assets, and how wealth is handled.',
    },
    'D3': {
        'tier': 'topic',
        'audience': 'advanced',
        'ai_eligible': False,
        'status': 'topic-specific',
        'plain_english': 'Courage, effort, initiative, and siblings.',
    },
    'D4': {
        'tier': 'topic',
        'audience': 'advanced',
        'ai_eligible': False,
        'status': 'topic-specific',
        'plain_english': 'Home, property, roots, and settlement.',
    },
    'D7': {
        'tier': 'topic',
        'audience': 'advanced',
        'ai_eligible': False,
        'status': 'use with birth-time care',
        'plain_english': 'Children, fertility, lineage, and creative offspring.',
    },
    'D9': {
        'tier': 'core',
        'audience': 'beginner',
        'ai_eligible': True,
        'status': 'core and verified',
        'plain_english': 'Marriage, deeper maturity, dharma, and the inner strength of planets.',
    },
    'D10': {
        'tier': 'core',
        'audience': 'beginner',
        'ai_eligible': True,
        'status': 'core and verified',
        'plain_english': 'Career, role, reputation, and professional direction.',
    },
    'D12': {
        'tier': 'topic',
        'audience': 'advanced',
        'ai_eligible': False,
        'status': 'topic-specific',
        'plain_english': 'Parents, ancestry, and inherited family patterns.',
    },
    'D16': {
        'tier': 'hidden',
        'audience': 'expert',
        'ai_eligible': False,
        'status': 'simplified formula',
        'plain_english': 'Comforts, vehicles, and luxuries.',
    },
    'D20': {
        'tier': 'hidden',
        'audience': 'expert',
        'ai_eligible': False,
        'status': 'simplified formula',
        'plain_english': 'Spiritual practice, devotion, and inner sadhana.',
    },
    'D24': {
        'tier': 'hidden',
        'audience': 'expert',
        'ai_eligible': False,
        'status': 'simplified formula',
        'plain_english': 'Education, study, learning path, and scholarship.',
    },
    'D27': {
        'tier': 'hidden',
        'audience': 'expert',
        'ai_eligible': False,
        'status': 'simplified formula',
        'plain_english': 'Inner strength, resilience, and weak spots.',
    },
    'D30': {
        'tier': 'hidden',
        'audience': 'expert',
        'ai_eligible': False,
        'status': 'hidden until verified',
        'plain_english': 'Troubles, faults, and vulnerability patterns.',
    },
    'D40': {
        'tier': 'hidden',
        'audience': 'expert',
        'ai_eligible': False,
        'status': 'hidden until verified',
        'plain_english': 'Maternal lineage and subtle background karma.',
    },
    'D45': {
        'tier': 'hidden',
        'audience': 'expert',
        'ai_eligible': False,
        'status': 'hidden until verified',
        'plain_english': 'Paternal lineage and inherited character patterns.',
    },
    'D60': {
        'tier': 'hidden',
        'audience': 'expert',
        'ai_eligible': False,
        'status': 'hidden until verified',
        'plain_english': 'Very fine karmic background; extremely birth-time sensitive.',
    },
}


def calculate_all_vargas(planet_longitudes: dict[str, float]) -> dict[str, dict[str, str]]:
    """Calculate all 15 divisional charts for all planets.

    Args:
        planet_longitudes: dict of {planet_name: longitude}

    Returns:
        dict of {varga_name: {planet_name: sign}}
    """
    results = {}
    for varga_id, (func, name, purpose) in VARGA_FUNCTIONS.items():
        varga_chart = {}
        for planet, lon in planet_longitudes.items():
            varga_chart[planet] = func(lon)
        results[varga_id] = {
            'name': name,
            'purpose': purpose,
            'signs': varga_chart
        }
    return results


def get_varga_signs(chart_data) -> dict[str, dict[str, str]]:
    """Get all varga signs from a ChartData object.

    Args:
        chart_data: ChartData object from ephemeris

    Returns:
        dict of {varga_id: {planet_name: sign}}
    """
    longitudes = {}
    for name, planet in chart_data.planets.items():
        longitudes[name] = planet.longitude
    # Include Ascendant
    if chart_data.ascendant:
        longitudes['Asc'] = chart_data.ascendant.longitude

    return calculate_all_vargas(longitudes)
