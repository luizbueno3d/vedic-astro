"""Guna Milan — Ashtakoota compatibility (36-point system)."""

KOOTA_EXPLANATIONS = {
    'Varna': 'Varna is the ego and spiritual compatibility factor. It shows whether values, refinement, and role expectations sit comfortably together.',
    'Vashya': 'Vashya shows mutual influence, responsiveness, and how naturally one adapts to the other.',
    'Tara': 'Tara reflects well-being, support, and whether the connection tends to protect or strain the flow of life.',
    'Yoni': 'Yoni relates to instinctive chemistry, attraction style, intimacy, and animal-level compatibility.',
    'Maitri': 'Maitri shows mental friendship and how naturally the two Moon-sign lords cooperate.',
    'Gana': 'Gana reflects temperament and behavioral style - whether both people approach life with similar emotional nature.',
    'Bhakoot': 'Bhakoot shows how the Moon signs relate by distance, especially for emotional harmony, prosperity, and domestic flow.',
    'Nadi': 'Nadi is traditionally linked to health, vitality, and biological compatibility, especially in marriage matching.',
    'TOTAL': 'The total score is the traditional Moon-based matching result. It is useful as a first filter, but not the final word on compatibility.',
}

# Varna (Ego) — 1 point max
VARNA = {0: 'Brahmin', 1: 'Kshatriya', 2: 'Vaishya', 3: 'Shudra'}
VARNA_ORDER = {'Brahmin': 3, 'Kshatriya': 2, 'Vaishya': 1, 'Shudra': 0}
RASHI_VARNA = {
    0: 'Kshatriya', 1: 'Vaishya', 2: 'Shudra', 3: 'Brahmin',     # Aries-Cancer
    4: 'Kshatriya', 5: 'Vaishya', 6: 'Shudra', 7: 'Brahmin',     # Leo-Scorpio
    8: 'Kshatriya', 9: 'Vaishya', 10: 'Shudra', 11: 'Brahmin',   # Sag-Pisces
}

# Vashya (Control) — 2 points max
# Groups: Quadruped, Human, Water, Keeta, Jungle
VASHYA_GROUPS = {
    0: 'quadruped', 1: 'quadruped', 5: 'human', 6: 'human',
    3: 'water', 7: 'water', 11: 'water',
    8: 'quadruped', 9: 'quadruped',
    2: 'human', 4: 'jungle', 10: 'jungle',
}

# Tara (Fortune) — 3 points max
# Count from boy's Moon to girl's Moon, then mod 9
# Same Tara (1,4,7) = 0, Enemy Tara (2,6,8) = 1.5, Friend Tara (3,5,9) = 3

# Yoni (Physical) — 4 points max
YONI_ANIMALS = {
    0: 'horse', 1: 'elephant', 2: 'sheep', 3: 'snake',
    4: 'deer', 5: 'cat', 6: 'goat', 7: 'buffalo',
    8: 'tiger', 9: 'monkey', 10: 'mongoose', 11: 'dog',
}
YONI_FRIENDLY = {
    'horse': ['elephant', 'deer'],
    'elephant': ['horse', 'sheep'],
    'sheep': ['elephant', 'monkey'],
    'snake': ['buffalo', 'cat'],
    'deer': ['horse', 'monkey'],
    'cat': ['snake', 'goat'],
    'goat': ['cat', 'buffalo'],
    'buffalo': ['snake', 'goat'],
    'tiger': ['dog', 'mongoose'],
    'monkey': ['sheep', 'deer'],
    'mongoose': ['tiger', 'dog'],
    'dog': ['tiger', 'mongoose'],
}

# Maitri (Friendship) — 5 points max
# Based on planetary friendship between Moon sign lords
PLANET_FRIENDS = {
    0: [4, 1],       # Aries (Mars): Sun, Moon
    1: [3, 5],       # Taurus (Venus): Mercury, Saturn
    2: [3, 4],       # Gemini (Mercury): Venus, Sun
    3: [1, 2],       # Cancer (Moon): Mars, Mercury
    4: [0, 3],       # Leo (Sun): Moon, Mars
    5: [2, 3],       # Virgo (Mercury): Venus, Saturn
    6: [2, 5],       # Libra (Venus): Mercury, Saturn
    7: [0, 4],       # Scorpio (Mars): Sun, Moon
    8: [4, 1],       # Sag (Jupiter): Sun, Moon
    9: [5, 2],       # Cap (Saturn): Mercury, Venus
    10: [5, 3],      # Aqua (Saturn): Mercury, Venus
    11: [1, 4],      # Pisces (Jupiter): Moon, Sun
}

# Gana (Temperament) — 6 points max
GANA = {
    0: 'deva', 1: 'manushya', 2: 'rakshasa', 3: 'deva',
    4: 'manushya', 5: 'rakshasa', 6: 'deva', 7: 'rakshasa',
    8: 'manushya', 9: 'rakshasa', 10: 'deva', 11: 'manushya',
}

# Bhakoot (Love/Wealth) — 7 points max
# 2/12, 5/9, 6/8 = 0 points (inauspicious)
# All others = 7 points

# Nadi (Health) — 8 points max
NADI = {
    0: 'adi', 1: 'madhya', 2: 'antya', 3: 'adi',
    4: 'madhya', 5: 'antya', 6: 'adi', 7: 'madhya',
    8: 'antya', 9: 'adi', 10: 'madhya', 11: 'antya',
}


def calculate_varna(moon_1: int, moon_2: int) -> dict:
    """Varna: 1 point if boy's varna >= girl's varna."""
    varna_1 = RASHI_VARNA[moon_1]
    varna_2 = RASHI_VARNA[moon_2]
    score = 1 if VARNA_ORDER[varna_1] >= VARNA_ORDER[varna_2] else 0
    return {'score': score, 'max': 1, 'detail': f'{varna_1} vs {varna_2}'}


def calculate_vashya(moon_1: int, moon_2: int) -> dict:
    """Vashya: 2 points if same group, 1 if semi-compatible."""
    g1 = VASHYA_GROUPS[moon_1]
    g2 = VASHYA_GROUPS[moon_2]
    if g1 == g2:
        return {'score': 2, 'max': 2, 'detail': f'Same group ({g1})'}
    elif {g1, g2} in [{'quadruped', 'jungle'}, {'human', 'water'}]:
        return {'score': 1, 'max': 2, 'detail': f'Semi-compatible ({g1} vs {g2})'}
    return {'score': 0, 'max': 2, 'detail': f'Incompatible ({g1} vs {g2})'}


def calculate_tara(moon_1: int, moon_2: int) -> dict:
    """Tara: Count from boy Moon to girl Moon, mod 9."""
    tara = ((moon_2 - moon_1) % 12 % 9) + 1
    if tara in (1, 4, 7):
        return {'score': 0, 'max': 3, 'detail': f'Tara {tara} (enemy)'}
    elif tara in (2, 6, 8):
        return {'score': 1.5, 'max': 3, 'detail': f'Tara {tara} (neutral)'}
    else:
        return {'score': 3, 'max': 3, 'detail': f'Tara {tara} (friendly)'}


def calculate_yoni(moon_1: int, moon_2: int) -> dict:
    """Yoni: Based on animal compatibility."""
    a1 = YONI_ANIMALS[moon_1]
    a2 = YONI_ANIMALS[moon_2]
    if a1 == a2:
        return {'score': 4, 'max': 4, 'detail': f'Same animal ({a1})'}
    elif a2 in YONI_FRIENDLY.get(a1, []):
        return {'score': 3, 'max': 4, 'detail': f'Friendly ({a1} - {a2})'}
    elif {a1, a2} in [{'tiger', 'buffalo'}, {'dog', 'deer'}, {'cat', 'rat'}]:
        return {'score': 0, 'max': 4, 'detail': f'Enemy ({a1} - {a2})'}
    return {'score': 2, 'max': 4, 'detail': f'Neutral ({a1} - {a2})'}


def calculate_maitri(moon_1: int, moon_2: int) -> dict:
    """Maitri: Planetary friendship between Moon sign lords."""
    friends_1 = PLANET_FRIENDS.get(moon_1, [])
    if moon_2 in friends_1:
        return {'score': 5, 'max': 5, 'detail': 'Great friends'}
    elif moon_2 == moon_1:
        return {'score': 5, 'max': 5, 'detail': 'Same lord'}
    return {'score': 0, 'max': 5, 'detail': 'Not friends'}


def calculate_gana(moon_1: int, moon_2: int) -> dict:
    """Gana: Temperament compatibility."""
    g1 = GANA[moon_1]
    g2 = GANA[moon_2]
    if g1 == g2:
        return {'score': 6, 'max': 6, 'detail': f'Same gana ({g1})'}
    elif {g1, g2} == {'deva', 'manushya'}:
        return {'score': 5, 'max': 6, 'detail': 'Deva-Manushya (good)'}
    elif {g1, g2} == {'deva', 'rakshasa'}:
        return {'score': 0, 'max': 6, 'detail': 'Deva-Rakshasa (difficult)'}
    elif {g1, g2} == {'manushya', 'rakshasa'}:
        return {'score': 0, 'max': 6, 'detail': 'Manushya-Rakshasa (difficult)'}
    return {'score': 3, 'max': 6, 'detail': f'{g1} vs {g2}'}


def calculate_bhakoot(moon_1: int, moon_2: int) -> dict:
    """Bhakoot: Check for inauspicious house distances."""
    dist = (moon_2 - moon_1) % 12
    inauspicious = {(2-1)%12, (5-1)%12, (6-1)%12, (11)%12, (8-1)%12, (7-1)%12}
    # 2/12 = dist 1 or 11, 5/9 = dist 4 or 8, 6/8 = dist 5 or 7
    bad = {1, 4, 5, 7, 8, 11}
    if dist in bad:
        return {'score': 0, 'max': 7, 'detail': f'Inauspicious distance ({dist+1}/12)'}
    return {'score': 7, 'max': 7, 'detail': f'Auspicious distance'}


def calculate_nadi(moon_1: int, moon_2: int) -> dict:
    """Nadi: Health/genetic compatibility."""
    n1 = NADI[moon_1]
    n2 = NADI[moon_2]
    if n1 == n2:
        return {'score': 0, 'max': 8, 'detail': f'Same nadi ({n1}) — health concern'}
    return {'score': 8, 'max': 8, 'detail': f'Different nadi ({n1} vs {n2})'}


def calculate_guna_milan(moon_1: int, moon_2: int) -> dict:
    """Calculate full Ashtakoota Guna Milan.

    Args:
        moon_1: rashi index (0-11) of person 1's Moon
        moon_2: rashi index (0-11) of person 2's Moon

    Returns:
        dict with all 8 koota scores and total
    """
    kootas = {
        'Varna': calculate_varna(moon_1, moon_2),
        'Vashya': calculate_vashya(moon_1, moon_2),
        'Tara': calculate_tara(moon_1, moon_2),
        'Yoni': calculate_yoni(moon_1, moon_2),
        'Maitri': calculate_maitri(moon_1, moon_2),
        'Gana': calculate_gana(moon_1, moon_2),
        'Bhakoot': calculate_bhakoot(moon_1, moon_2),
        'Nadi': calculate_nadi(moon_1, moon_2),
    }

    total = sum(k['score'] for k in kootas.values())
    max_total = sum(k['max'] for k in kootas.values())

    # Interpretation
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
