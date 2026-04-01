"""Jaimini Astrology — Chara Karakas, Chara Dasha, Jaimini Raja Yoga.

Jaimini is a different system from Parashari (standard Vedic).
Key differences:
- Chara Karakas (7 movable significators based on degree, not nature)
- Chara Dasha (sign-based dasha, not planet-based)
- Jaimini Raja Yoga (from Atmakaraka and Amatyakaraka)
- Chara aspects (sign-based, not planet-based)
"""

from dataclasses import dataclass


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
    Rahu is included but counted in reverse (highest degree = lowest karaka).

    Args:
        planets: dict of {name: PlanetPosition} with .degree_in_sign attribute

    Returns:
        dict of {karaka_name: {'planet': name, 'degree': float, 'sign': str, ...}}
    """
    # Collect degrees for 7 classical planets + Rahu
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

    # Add Rahu (counted in reverse for degree comparison)
    if 'Rahu' in planets:
        p = planets['Rahu']
        degrees.append({
            'planet': 'Rahu',
            'degree': p.degree_in_sign,
            'sign': p.rashi,
            'sign_index': p.rashi_index,
            'house': p.house,
            'nakshatra': p.nakshatra,
            'pada': p.pada,
            'retrograde': False,
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
        'Rahu': (
            "Your Atmakaraka is Rahu — the north node, the planet of desire and obsession. "
            "Your soul's purpose is to break boundaries and explore the unknown."
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
        'Rahu': 'Your spouse is unconventional — from a different background, culture, or field. They bring excitement and the unexpected.',
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

    # Jaimini sign aspects
    movable = {0, 3, 6, 9}   # Aries, Cancer, Libra, Capricorn
    fixed = {1, 4, 7, 10}     # Taurus, Leo, Scorpio, Aquarius
    dual = {2, 5, 8, 11}      # Gemini, Virgo, Sagittarius, Pisces

    aspects_ak = False
    if amk_sign in movable:
        # Movable aspects all fixed signs except adjacent
        aspects_ak = ak_sign in fixed and abs(ak_sign - amk_sign) not in [1, 11]
    elif amk_sign in fixed:
        # Fixed aspects all movable signs except adjacent
        aspects_ak = ak_sign in movable and abs(ak_sign - amk_sign) not in [1, 11]
    elif amk_sign in dual:
        # Dual aspects other dual signs
        aspects_ak = ak_sign in dual and ak_sign != amk_sign

    if aspects_ak:
        yogas.append({
            'name': 'Jaimini Raja Yoga',
            'description': f'Amatyakaraka ({amk["planet"]}) aspects Atmakaraka ({ak["planet"]}) sign. '
                           f'This creates a direct connection between your soul purpose and career action.',
            'planets': [ak['planet'], amk['planet']],
            'strength': 'strong',
        })

    return yogas


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
