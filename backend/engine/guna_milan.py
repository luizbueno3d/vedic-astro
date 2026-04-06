"""Guna Milan — Ashtakoota compatibility (36-point system).

This implementation uses Moon sign plus Moon nakshatra data, which is the correct
base for classical Ashtakoota matching. It is still a practical app-oriented
version, but much closer to traditional matching than the older sign-only logic.
"""

from .ephemeris import PlanetPosition, RASHI_LORDS

KOOTA_EXPLANATIONS = {
    'Varna': 'Varna is the spiritual and ego compatibility factor. It asks whether values, refinement, and role expectations sit comfortably together.',
    'Vashya': 'Vashya shows mutual influence, control, responsiveness, and how easily one adapts to the other.',
    'Tara': 'Tara reflects well-being, support, and whether the connection tends to protect, nourish, or strain the flow of life.',
    'Yoni': 'Yoni relates to instinctive chemistry, sexual style, bodily comfort, and animal-level compatibility.',
    'Maitri': 'Maitri shows mental friendship and whether the two Moon-sign lords naturally cooperate or feel distant.',
    'Gana': 'Gana reflects temperament and behavioral style - whether both people approach life with similar emotional nature or very different instincts.',
    'Bhakoot': 'Bhakoot shows how the Moon signs relate by distance, especially for emotional harmony, prosperity, and domestic flow over time.',
    'Nadi': 'Nadi is traditionally linked to health, vitality, and biological compatibility, especially in marriage matching and family-building concerns.',
    'TOTAL': 'The total score is the traditional Moon-based matching result. It is a useful first filter for temperament and traditional marriage matching, but it is not the final word on full compatibility.',
}

RASHI_VARNA = {
    0: 'Kshatriya', 1: 'Vaishya', 2: 'Shudra', 3: 'Brahmin',
    4: 'Kshatriya', 5: 'Vaishya', 6: 'Shudra', 7: 'Brahmin',
    8: 'Kshatriya', 9: 'Vaishya', 10: 'Shudra', 11: 'Brahmin',
}
VARNA_ORDER = {'Brahmin': 3, 'Kshatriya': 2, 'Vaishya': 1, 'Shudra': 0}

NAKSHATRA_GANA = {
    0: 'deva', 1: 'manushya', 2: 'rakshasa', 3: 'manushya', 4: 'deva', 5: 'manushya',
    6: 'deva', 7: 'deva', 8: 'rakshasa', 9: 'rakshasa', 10: 'manushya', 11: 'manushya',
    12: 'deva', 13: 'rakshasa', 14: 'deva', 15: 'rakshasa', 16: 'deva', 17: 'rakshasa',
    18: 'rakshasa', 19: 'manushya', 20: 'manushya', 21: 'deva', 22: 'rakshasa', 23: 'rakshasa',
    24: 'manushya', 25: 'manushya', 26: 'deva',
}

NAKSHATRA_NADI = {
    0: 'adi',      # Ashwini
    1: 'madhya',   # Bharani
    2: 'antya',    # Krittika
    3: 'antya',    # Rohini
    4: 'madhya',   # Mrigashira
    5: 'adi',      # Ardra
    6: 'adi',      # Punarvasu
    7: 'madhya',   # Pushya
    8: 'antya',    # Ashlesha
    9: 'antya',    # Magha
    10: 'madhya',  # Purva Phalguni
    11: 'adi',     # Uttara Phalguni
    12: 'adi',     # Hasta
    13: 'madhya',  # Chitra
    14: 'antya',   # Swati
    15: 'antya',   # Vishakha
    16: 'madhya',  # Anuradha
    17: 'adi',     # Jyeshtha
    18: 'adi',     # Mula
    19: 'madhya',  # Purva Ashadha
    20: 'antya',   # Uttara Ashadha
    21: 'antya',   # Shravana
    22: 'madhya',  # Dhanishta
    23: 'adi',     # Shatabhisha
    24: 'adi',     # Purva Bhadrapada
    25: 'madhya',  # Uttara Bhadrapada
    26: 'antya',   # Revati
}

NAKSHATRA_YONI = {
    0: 'horse', 1: 'elephant', 2: 'sheep', 3: 'serpent', 4: 'serpent', 5: 'dog', 6: 'cat', 7: 'sheep', 8: 'cat',
    9: 'rat', 10: 'rat', 11: 'cow', 12: 'buffalo', 13: 'tiger', 14: 'buffalo', 15: 'tiger', 16: 'deer', 17: 'deer',
    18: 'dog', 19: 'monkey', 20: 'mongoose', 21: 'monkey', 22: 'lion', 23: 'horse', 24: 'lion', 25: 'cow', 26: 'elephant',
}

YONI_FRIENDLY = {
    'horse': {'elephant', 'horse'}, 'elephant': {'horse', 'elephant'},
    'sheep': {'sheep', 'monkey'}, 'serpent': {'serpent', 'cat'},
    'dog': {'dog', 'deer'}, 'cat': {'cat', 'serpent'},
    'rat': {'rat', 'cow'}, 'cow': {'cow', 'buffalo', 'rat'},
    'buffalo': {'buffalo', 'cow'}, 'tiger': {'tiger', 'lion'},
    'deer': {'deer', 'dog'}, 'monkey': {'monkey', 'sheep'},
    'mongoose': {'mongoose', 'lion'}, 'lion': {'lion', 'tiger', 'mongoose'},
}
YONI_ENEMIES = {
    frozenset({'serpent', 'mongoose'}), frozenset({'lion', 'elephant'}), frozenset({'cow', 'tiger'}),
    frozenset({'horse', 'buffalo'}), frozenset({'dog', 'tiger'}), frozenset({'cat', 'rat'}),
}

PLANET_REL = {
    'Sun': {'friends': {'Moon', 'Mars', 'Jupiter'}, 'neutral': {'Mercury'}, 'enemies': {'Venus', 'Saturn'}},
    'Moon': {'friends': {'Sun', 'Mercury'}, 'neutral': {'Mars', 'Jupiter', 'Venus', 'Saturn'}, 'enemies': set()},
    'Mars': {'friends': {'Sun', 'Moon', 'Jupiter'}, 'neutral': {'Venus', 'Saturn'}, 'enemies': {'Mercury'}},
    'Mercury': {'friends': {'Sun', 'Venus'}, 'neutral': {'Mars', 'Jupiter', 'Saturn'}, 'enemies': {'Moon'}},
    'Jupiter': {'friends': {'Sun', 'Moon', 'Mars'}, 'neutral': {'Saturn'}, 'enemies': {'Mercury', 'Venus'}},
    'Venus': {'friends': {'Mercury', 'Saturn'}, 'neutral': {'Mars', 'Jupiter'}, 'enemies': {'Sun', 'Moon'}},
    'Saturn': {'friends': {'Mercury', 'Venus'}, 'neutral': {'Jupiter'}, 'enemies': {'Sun', 'Moon', 'Mars'}},
}

VASHYA_CATEGORY_NAMES = {
    'quadruped': 'quadruped',
    'human': 'human',
    'water': 'water',
    'wild': 'wild',
    'insect': 'insect',
}

VASHYA_MATRIX = {
    ('quadruped', 'quadruped'): 2,
    ('human', 'human'): 2,
    ('water', 'water'): 2,
    ('wild', 'wild'): 2,
    ('insect', 'insect'): 2,
    ('quadruped', 'human'): 1,
    ('quadruped', 'water'): 1,
    ('quadruped', 'insect'): 1,
    ('human', 'water'): 1,
    ('human', 'wild'): 1,
    ('water', 'insect'): 1,
    ('human', 'insect'): 1,
}


def _vashya_category(moon: PlanetPosition) -> str:
    sign = moon.rashi_index
    deg = moon.degree_in_sign
    if sign == 4:
        return 'wild'
    if sign == 7:
        return 'insect'
    if sign in {0, 1}:
        return 'quadruped'
    if sign in {2, 5, 6, 10}:
        return 'human'
    if sign in {3, 11}:
        return 'water'
    if sign == 8:
        return 'human' if deg < 15 else 'quadruped'
    if sign == 9:
        return 'quadruped' if deg < 15 else 'water'
    return 'human'


def _planet_relation_score(lord_1: str, lord_2: str) -> float:
    if lord_1 == lord_2:
        return 5
    rel1 = PLANET_REL[lord_1]
    rel2 = PLANET_REL[lord_2]
    if lord_2 in rel1['friends'] and lord_1 in rel2['friends']:
        return 5
    if (lord_2 in rel1['friends'] and lord_1 in rel2['neutral']) or (lord_1 in rel2['friends'] and lord_2 in rel1['neutral']):
        return 4
    if lord_2 in rel1['neutral'] and lord_1 in rel2['neutral']:
        return 3
    if (lord_2 in rel1['friends'] and lord_1 in rel2['enemies']) or (lord_1 in rel2['friends'] and lord_2 in rel1['enemies']):
        return 1
    if lord_2 in rel1['enemies'] and lord_1 in rel2['enemies']:
        return 0
    return 3


def calculate_varna(bride_moon: PlanetPosition, groom_moon: PlanetPosition) -> dict:
    bride_varna = RASHI_VARNA[bride_moon.rashi_index]
    groom_varna = RASHI_VARNA[groom_moon.rashi_index]
    score = 1 if VARNA_ORDER[groom_varna] >= VARNA_ORDER[bride_varna] else 0
    return {'score': score, 'max': 1, 'detail': f'{bride_varna} vs {groom_varna}'}


def calculate_vashya(bride_moon: PlanetPosition, groom_moon: PlanetPosition) -> dict:
    g1 = _vashya_category(bride_moon)
    g2 = _vashya_category(groom_moon)
    score = VASHYA_MATRIX.get((g1, g2), VASHYA_MATRIX.get((g2, g1), 0))
    detail_map = {2: 'Same or strongly compatible', 1: 'Semi-compatible', 0: 'Incompatible'}
    return {'score': score, 'max': 2, 'detail': f"{detail_map[score]} ({VASHYA_CATEGORY_NAMES[g1]} vs {VASHYA_CATEGORY_NAMES[g2]})"}


def calculate_tara(bride_moon: PlanetPosition, groom_moon: PlanetPosition) -> dict:
    count_bg = (groom_moon.nakshatra_index - bride_moon.nakshatra_index) % 27 + 1
    count_gb = (bride_moon.nakshatra_index - groom_moon.nakshatra_index) % 27 + 1
    rem_bg = count_bg % 9 or 9
    rem_gb = count_gb % 9 or 9
    good = {2, 4, 6, 8, 9}
    good_count = int(rem_bg in good) + int(rem_gb in good)
    score = 3 if good_count == 2 else 1.5 if good_count == 1 else 0
    quality = 'friendly' if score == 3 else 'neutral' if score == 1.5 else 'enemy'
    return {'score': score, 'max': 3, 'detail': f'Tara {rem_bg}/{rem_gb} ({quality})'}


def calculate_yoni(bride_moon: PlanetPosition, groom_moon: PlanetPosition) -> dict:
    a1 = NAKSHATRA_YONI[bride_moon.nakshatra_index]
    a2 = NAKSHATRA_YONI[groom_moon.nakshatra_index]
    if a1 == a2:
        score = 4
        label = 'Same animal'
    elif a2 in YONI_FRIENDLY.get(a1, set()) or a1 in YONI_FRIENDLY.get(a2, set()):
        score = 3
        label = 'Friendly'
    elif frozenset({a1, a2}) in YONI_ENEMIES:
        score = 0
        label = 'Enemy'
    else:
        score = 2
        label = 'Neutral'
    return {'score': score, 'max': 4, 'detail': f'{label} ({a1} - {a2})'}


def calculate_maitri(bride_moon: PlanetPosition, groom_moon: PlanetPosition) -> dict:
    lord_1 = RASHI_LORDS[bride_moon.rashi_index]
    lord_2 = RASHI_LORDS[groom_moon.rashi_index]
    score = _planet_relation_score(lord_1, lord_2)
    if score == 5:
        detail = 'Great friends'
    elif score == 4:
        detail = 'Friendly / supportive'
    elif score == 3:
        detail = 'Neutral'
    elif score == 1:
        detail = 'Mixed friendship'
    else:
        detail = 'Not friends'
    return {'score': score, 'max': 5, 'detail': detail}


def calculate_gana(bride_moon: PlanetPosition, groom_moon: PlanetPosition) -> dict:
    g1 = NAKSHATRA_GANA[bride_moon.nakshatra_index]
    g2 = NAKSHATRA_GANA[groom_moon.nakshatra_index]
    if g1 == g2:
        score, detail = 6, f'Same gana ({g1})'
    elif {g1, g2} == {'deva', 'manushya'}:
        # Mainstream app implementations often treat Deva-Manushya as fully compatible.
        score, detail = 6, 'Deva-Manushya (good)'
    elif {g1, g2} == {'manushya', 'rakshasa'}:
        score, detail = 1, 'Manushya-Rakshasa (difficult)'
    else:
        score, detail = 0, 'Deva-Rakshasa (difficult)'
    return {'score': score, 'max': 6, 'detail': detail}


def calculate_bhakoot(bride_moon: PlanetPosition, groom_moon: PlanetPosition) -> dict:
    dist = (groom_moon.rashi_index - bride_moon.rashi_index) % 12
    bad = {1, 4, 5, 7, 8, 11}
    if dist in bad:
        return {'score': 0, 'max': 7, 'detail': f'Inauspicious distance ({dist+1}/12)'}
    return {'score': 7, 'max': 7, 'detail': 'Auspicious distance'}


def calculate_nadi(bride_moon: PlanetPosition, groom_moon: PlanetPosition) -> dict:
    n1 = NAKSHATRA_NADI[bride_moon.nakshatra_index]
    n2 = NAKSHATRA_NADI[groom_moon.nakshatra_index]
    if n1 == n2:
        return {'score': 0, 'max': 8, 'detail': f'Same nadi ({n1}) — health concern'}
    return {'score': 8, 'max': 8, 'detail': f'Different nadi ({n1} vs {n2})'}


def calculate_guna_milan(bride_moon: PlanetPosition, groom_moon: PlanetPosition) -> dict:
    """Calculate full Ashtakoota using Moon sign + nakshatra data.

    Note: this function expects bride/girl as first argument and groom/boy as second,
    following the traditional direction of Guna Milan.
    """
    kootas = {
        'Varna': calculate_varna(bride_moon, groom_moon),
        'Vashya': calculate_vashya(bride_moon, groom_moon),
        'Tara': calculate_tara(bride_moon, groom_moon),
        'Yoni': calculate_yoni(bride_moon, groom_moon),
        'Maitri': calculate_maitri(bride_moon, groom_moon),
        'Gana': calculate_gana(bride_moon, groom_moon),
        'Bhakoot': calculate_bhakoot(bride_moon, groom_moon),
        'Nadi': calculate_nadi(bride_moon, groom_moon),
    }

    total = sum(k['score'] for k in kootas.values())
    max_total = sum(k['max'] for k in kootas.values())

    if total >= 28:
        verdict = 'Excellent match — highly compatible'
    elif total >= 24:
        verdict = 'Good match — compatible with minor adjustments'
    elif total >= 18:
        verdict = 'Average match — some challenges but workable'
    elif total >= 12:
        verdict = 'Below average — significant differences to address'
    else:
        verdict = 'Poor match — major incompatibilities'

    return {
        'kootas': kootas,
        'total': total,
        'max': max_total,
        'percentage': round(total / max_total * 100, 1),
        'verdict': verdict,
        'explanations': KOOTA_EXPLANATIONS,
    }
