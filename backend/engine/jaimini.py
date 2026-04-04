"""Jaimini Astrology — Chara Karakas, sign aspects, Karakamsa, and Raja Yoga.

Jaimini is a different system from Parashari (standard Vedic).
Key differences:
- Chara Karakas (7 movable significators based on degree, not nature)
- Chara Dasha (sign-based dasha, not planet-based)
- Jaimini Raja Yoga (from Atmakaraka and Amatyakaraka)
- Chara aspects (sign-based, not planet-based)
"""

from .charts import d9_navamsha
from .ephemeris import RASHIS

MOVABLE_SIGNS = {0, 3, 6, 9}
FIXED_SIGNS = {1, 4, 7, 10}
DUAL_SIGNS = {2, 5, 8, 11}


# Chara Karaka roles
KARAKA_ROLES = {
    'Atmakaraka': {'short': 'AK', 'meaning': 'Soul significator — your deepest purpose and identity'},
    'Amatyakaraka': {'short': 'AmK', 'meaning': 'Career/assistant — what you do and who supports you'},
    'Bhratrukaraka': {'short': 'BK', 'meaning': 'Siblings/courage — your relationship with siblings and bravery'},
    'Matrukaraka': {'short': 'MK', 'meaning': 'Mother/nurturing — your relationship with mother and comfort'},
    'Putrakaraka': {'short': 'PK', 'meaning': 'Children/creativity — your creative expression and offspring'},
    'Gnatikaraka': {'short': 'GK', 'meaning': 'Enemies/relatives — challenges and extended family'},
    'Darakaraka': {'short': 'DK', 'meaning': 'Spouse/partner — what you seek in a partner'},
}

# Karaka order (7 classical planets only, no nodes)
KARAKA_NAMES = ['Atmakaraka', 'Amatyakaraka', 'Bhratrukaraka', 'Matrukaraka',
                'Putrakaraka', 'Gnatikaraka', 'Darakaraka']


def calculate_chara_karakas(planets: dict) -> dict:
    """Calculate Jaimini Chara Karakas.

    The planet with the HIGHEST degree (within its sign) is the Atmakaraka.
    Second highest = Amatyakaraka, and so on.
    This implementation follows the 7 classical chara karakas only:
    Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn.
    Rahu and Ketu do not participate.

    Args:
        planets: dict of {name: PlanetPosition} with .degree_in_sign attribute

    Returns:
        dict of {karaka_name: {'planet': name, 'degree': float, 'sign': str, ...}}
    """
    # Collect degrees for the 7 classical planets only.
    degrees = []
    for name in ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']:
        if name in planets:
            p = planets[name]
            degrees.append({
                'planet': name,
                'degree': p.degree_in_sign,
                'sign': p.rashi,
                'sign_index': p.rashi_index,
                'house': p.house,
                'nakshatra': p.nakshatra,
                'pada': p.pada,
                'retrograde': p.retrograde,
            })

    # Sort by degree (highest first)
    degrees.sort(key=lambda x: x['degree'], reverse=True)

    # Assign karakas
    result = {}
    for i, karaka_name in enumerate(KARAKA_NAMES):
        if i < len(degrees):
            result[karaka_name] = degrees[i]

    return result


def interpret_atmakaraka(ak_data: dict) -> str:
    """Deep interpretation of Atmakaraka — the soul's purpose."""
    planet = ak_data['planet']
    sign = ak_data['sign']
    house = ak_data['house']
    nak = ak_data['nakshatra']
    retro = ak_data.get('retrograde', False)

    # Atmakaraka interpretations by planet
    ak_meanings = {
        'Saturn': (
            "Your Atmakaraka is Saturn — the planet of time, discipline, and karma. "
            "This means your SOUL'S PURPOSE is mastery through patience and endurance. "
            "You are here to learn that everything worthwhile takes time. "
            "Saturn as AK doesn't give you shortcuts — it gives you DEPTH. "
            "Every challenge you face is designed to build something lasting in you."
        ),
        'Mars': (
            "Your Atmakaraka is Mars — the planet of action, courage, and competition. "
            "Your soul's purpose is to ACT, to compete, to build with your own hands."
        ),
        'Jupiter': (
            "Your Atmakaraka is Jupiter — the planet of wisdom, teaching, and expansion. "
            "Your soul's purpose is to learn, teach, and expand consciousness."
        ),
        'Venus': (
            "Your Atmakaraka is Venus — the planet of love, beauty, and harmony. "
            "Your soul's purpose is to create beauty and experience love in its highest form."
        ),
        'Mercury': (
            "Your Atmakaraka is Mercury — the planet of communication and analysis. "
            "Your soul's purpose is to understand, communicate, and connect through knowledge."
        ),
        'Sun': (
            "Your Atmakaraka is the Sun — the planet of authority and self-expression. "
            "Your soul's purpose is to shine, lead, and express your authentic self."
        ),
        'Moon': (
            "Your Atmakaraka is the Moon — the planet of emotions and nurturing. "
            "Your soul's purpose is to feel deeply and nurture others."
        ),
    }

    text = ak_meanings.get(planet, f"Your Atmakaraka is {planet}.")

    # Placement specifics
    text += f"\n\nIt sits in {sign}, House {house} ({nak}). "
    house_ak_meanings = {
        1: "Your soul's purpose is deeply personal — it's about WHO YOU ARE.",
        2: "Your soul works through wealth, speech, and family values.",
        3: "Your soul works through skills, communication, and courage.",
        4: "Your soul works through home, mother, and emotional foundations.",
        5: "Your soul works through creativity, children, and intelligence.",
        6: "Your soul works through service, health, and overcoming obstacles.",
        7: "Your soul works through partnerships and relationships.",
        8: "Your soul works through transformation, research, and the occult.",
        9: "Your soul works through dharma, teaching, and higher wisdom.",
        10: "Your soul works through career and public recognition.",
        11: "Your soul works through networks, gains, and fulfillment of desires.",
        12: "Your soul works through surrender, spirituality, and foreign connections.",
    }
    text += house_ak_meanings.get(house, "")

    if retro:
        text += "\n\nRetrograde Atmakaraka: Your soul's lessons are processed INTERNALLY first. You learn through reflection, not just experience. Your wisdom comes from going within."

    return text


def interpret_darakaraka(dk_data: dict) -> str:
    """Interpretation of Darakaraka — the spouse significator."""
    planet = dk_data['planet']
    sign = dk_data['sign']
    house = dk_data['house']

    dk_meanings = {
        'Sun': 'Your spouse has solar qualities — authoritative, confident, creative. They may be in a leadership role or connected to government/authority. They bring warmth and vitality to the relationship.',
        'Moon': 'Your spouse has lunar qualities — nurturing, emotional, protective. They may be connected to public life, care work, or the home. They bring emotional depth.',
        'Mars': 'Your spouse has Martian qualities — energetic, competitive, action-oriented. They may be in engineering, sports, or military. They bring drive and passion.',
        'Mercury': 'Your spouse has Mercurial qualities — intelligent, communicative, youthful. They may be in business, writing, or teaching. They bring mental stimulation.',
        'Jupiter': 'Your spouse has Jupiterian qualities — wise, generous, philosophical. They may be in teaching, law, or spirituality. They bring wisdom and expansion.',
        'Venus': 'Your spouse has Venusian qualities — beautiful, artistic, diplomatic. They may be in arts, beauty, or diplomacy. They bring harmony and charm.',
        'Saturn': 'Your spouse has Saturnian qualities — disciplined, mature, responsible. They may be older in spirit or experience. They bring structure and commitment.',
    }

    text = dk_meanings.get(planet, f'Your Darakaraka is {planet}.')
    text += f'\n\nDarakaraka in {sign}, House {house}.'

    return text


def calculate_jaimini_raja_yoga(karakas: dict) -> list[dict]:
    """Jaimini Raja Yoga: Atmakaraka in a sign aspected by Amatyakaraka's sign lord.

    Jaimini aspects are sign-based:
    - Movable signs aspect Fixed signs (except adjacent)
    - Fixed signs aspect Movable signs (except adjacent)
    - Dual signs aspect other Dual signs
    """
    yogas = []

    ak = karakas.get('Atmakaraka')
    amk = karakas.get('Amatyakaraka')

    if not ak or not amk:
        return yogas

    # Check if AmK aspects AK's sign
    ak_sign = ak['sign_index']
    amk_sign = amk['sign_index']

    aspects_ak = ak_sign in get_jaimini_aspect_signs(amk_sign)

    if aspects_ak:
        yogas.append({
            'name': 'Jaimini Raja Yoga',
            'description': f'Amatyakaraka ({amk["planet"]}) aspects Atmakaraka ({ak["planet"]}) sign. '
                           f'This creates a direct connection between your soul purpose and career action.',
            'planets': [ak['planet'], amk['planet']],
            'strength': 'strong',
        })

    return yogas


def get_jaimini_aspect_signs(sign_index: int) -> list[int]:
    """Return sign indices aspected by a sign via Jaimini rasi drishti."""
    if sign_index in MOVABLE_SIGNS:
        return [idx for idx in FIXED_SIGNS if (idx - sign_index) % 12 not in (1, 11)]
    if sign_index in FIXED_SIGNS:
        return [idx for idx in MOVABLE_SIGNS if (idx - sign_index) % 12 not in (1, 11)]
    return [idx for idx in DUAL_SIGNS if idx != sign_index]


def get_jaimini_sign_aspects(planets: dict) -> list[dict]:
    """Return sign-based Jaimini aspects between occupied signs."""
    results = []
    seen = set()
    for from_name, from_planet in planets.items():
        target_signs = set(get_jaimini_aspect_signs(from_planet.rashi_index))
        for to_name, to_planet in planets.items():
            if from_name == to_name:
                continue
            if to_planet.rashi_index not in target_signs:
                continue
            key = (from_name, to_name)
            if key in seen:
                continue
            seen.add(key)
            results.append({
                'from': from_name,
                'from_sign': from_planet.rashi,
                'to': to_name,
                'to_sign': to_planet.rashi,
                'type': 'Jaimini Rasi Drishti',
            })
    return results


def calculate_karakamsa(karakas: dict, planets: dict) -> dict:
    """Calculate Swamsa/Karakamsa from Atmakaraka Navamsha sign.

    Swamsa = AK's sign in D9.
    Karakamsa = that same sign used as a reference lagna in D1.
    """
    ak = karakas.get('Atmakaraka')
    if not ak:
        return {}

    ak_planet_name = ak['planet']
    ak_planet = planets.get(ak_planet_name)
    if not ak_planet:
        return {}

    swamsa_sign = d9_navamsha(ak_planet.longitude)
    swamsa_idx = RASHIS.index(swamsa_sign)

    occupants = []
    aspected_by = []
    tenth_from = ((9 + swamsa_idx) % 12) + 1
    seventh_from = ((6 + swamsa_idx) % 12) + 1

    for name, planet in planets.items():
        karakamsa_house = ((planet.rashi_index - swamsa_idx) % 12) + 1
        if karakamsa_house == 1:
            occupants.append(name)
        if swamsa_idx in get_jaimini_aspect_signs(planet.rashi_index):
            aspected_by.append(name)

    return {
        'atmakaraka': ak_planet_name,
        'swamsa_sign': swamsa_sign,
        'karakamsa_sign': swamsa_sign,
        'karakamsa_sign_index': swamsa_idx,
        'occupants': occupants,
        'aspected_by': sorted(set(aspected_by)),
        'tenth_from_karakamsa': RASHIS[(swamsa_idx + 9) % 12],
        'seventh_from_karakamsa': RASHIS[(swamsa_idx + 6) % 12],
        'planet_houses': {
            name: ((planet.rashi_index - swamsa_idx) % 12) + 1
            for name, planet in planets.items()
        },
    }


def interpret_karakamsa(karakamsa: dict) -> str:
    """Beginner-friendly Karakamsa explanation."""
    if not karakamsa:
        return 'Karakamsa could not be calculated.'

    parts = [
        f"Karakamsa is in {karakamsa['karakamsa_sign']}. This means the Atmakaraka's Navamsha sign is {karakamsa['swamsa_sign']}, and that sign becomes a Jaimini reference lagna for soul direction.",
    ]
    if karakamsa['occupants']:
        parts.append(f"Planets in Karakamsa: {', '.join(karakamsa['occupants'])}. These directly color the soul-path expression.")
    if karakamsa['aspected_by']:
        parts.append(f"Jaimini sign aspects to Karakamsa come from: {', '.join(karakamsa['aspected_by'])}. These planets shape how the soul-direction unfolds.")
    parts.append(f"The 10th from Karakamsa is {karakamsa['tenth_from_karakamsa']}, useful for vocation; the 7th from Karakamsa is {karakamsa['seventh_from_karakamsa']}, useful for partnership themes.")
    return ' '.join(parts)


def get_karakas_summary(karakas: dict) -> str:
    """Generate a readable summary of all Chara Karakas."""
    lines = []
    lines.append("JAIMINI CHARA KARAKAS (7 Movable Significators):")
    for role in KARAKA_NAMES:
        if role in karakas:
            k = karakas[role]
            info = KARAKA_ROLES[role]
            lines.append(f"  {info['short']} {role}: {k['planet']} ({k['degree']:.2f}° in {k['sign']}, H{k['house']}) — {info['meaning']}")
    return "\n".join(lines)


def get_karakas_priority_notes(karakas: dict) -> str:
    """Readable Jaimini notes for interpretation prompts."""
    lines = []
    lines.append('JAIMINI PRIORITY NOTES:')
    lines.append('  Read Atmakaraka first for soul-pressure and core lesson.')
    lines.append('  Read Amatyakaraka second for vocation, implementation, and worldly role.')
    lines.append('  Read Darakaraka for spouse/partnership pattern.')
    lines.append('  Remaining karakas refine siblings, mother, children/creativity, and conflict/relatives.')
    for role in ['Atmakaraka', 'Amatyakaraka', 'Darakaraka', 'Putrakaraka', 'Matrukaraka', 'Bhratrukaraka', 'Gnatikaraka']:
        if role in karakas:
            k = karakas[role]
            lines.append(f"  {role}: {k['planet']} in {k['sign']} H{k['house']}")
    return "\n".join(lines)


def get_jaimini_interpretation(karakas: dict) -> dict:
    """Get full Jaimini interpretation."""
    result = {}

    if 'Atmakaraka' in karakas:
        result['atmakaraka'] = interpret_atmakaraka(karakas['Atmakaraka'])

    if 'Darakaraka' in karakas:
        result['darakaraka'] = interpret_darakaraka(karakas['Darakaraka'])

    result['raja_yogas'] = calculate_jaimini_raja_yoga(karakas)
    result['summary'] = get_karakas_summary(karakas)

    return result
