"""Bhavat Bhavam — House-from-house analysis.

Each house has a Bhavat Bhavam relationship with another house.
Bhavat Bhavam means "house of the house" — you analyze a house by
looking at the same-numbered house from that house.

For example:
- Bhavat Bhavam of H2 = H2 from H2 = H3 (2nd from 2nd)
- Bhavat Bhavam of H7 = H7 from H7 = H1 (7th from 7th)

This creates deeper layers of meaning for each house.
"""

# Bhavat Bhavam mapping: house → bhavat bhavam house
# Formula: BH(h) = (h + h - 2) % 12 + 1 = (2h - 2) % 12 + 1
# Or simply: count h houses forward from house h
BHAVAT_BHAVAM = {
    1: 1,    # 1st from 1st = 1st (self about self)
    2: 3,    # 2nd from 2nd = 3rd (wealth through courage/siblings)
    3: 5,    # 3rd from 3rd = 5th (courage through creativity)
    4: 7,    # 4th from 4th = 7th (home through partnerships)
    5: 9,    # 5th from 5th = 9th (creativity through dharma)
    6: 11,   # 6th from 6th = 11th (enemies through gains)
    7: 1,    # 7th from 7th = 1st (partners through self)
    8: 3,    # 8th from 8th = 3rd (transformation through courage)
    9: 5,    # 9th from 9th = 5th (dharma through creativity)
    10: 7,   # 10th from 10th = 7th (career through partnerships)
    11: 9,   # 11th from 11th = 9th (gains through dharma)
    12: 11,  # 12th from 12th = 11th (losses through gains)
}

# Interpretation of each Bhavat Bhavam relationship
INTERPRETATIONS = {
    1: {
        'title': 'Self — Reinforced Self',
        'description': 'The self is analyzed through itself. H1 Bhavat Bhavam = H1 means your identity is self-referential — who you are is deeply connected to how you see yourself. Planets here amplify your core personality.'
    },
    2: {
        'title': 'Wealth — Through Courage & Siblings',
        'description': 'Your wealth (H2) is connected to your courage, skills, and younger siblings (H3). Money comes through your own efforts, communication, and short journeys. The 3rd house is the Bhavat Bhavam of wealth.'
    },
    3: {
        'title': 'Courage — Through Creativity & Children',
        'description': 'Your courage and skills (H3) are connected to creativity, romance, and children (H5). Bravery is expressed through artistic or romantic pursuits. Skills are refined through creative practice.'
    },
    4: {
        'title': 'Home — Through Partnerships',
        'description': 'Your home and mother (H4) are connected to partnerships and marriage (H7). Domestic happiness comes through your partner. Your mother may influence your choice of partner, or vice versa.'
    },
    5: {
        'title': 'Creativity — Through Dharma & Fortune',
        'description': 'Your creativity and children (H5) are connected to dharma, higher learning, and fortune (H9). Creative expression follows your life purpose. Children bring good fortune.'
    },
    6: {
        'title': 'Enemies — Through Gains & Networks',
        'description': 'Your enemies and health (H6) are connected to gains and social networks (H11). Enemies may come through your social circle. Health improves through group activities. Victory over enemies brings gains.'
    },
    7: {
        'title': 'Partnerships — Through Self',
        'description': 'Your partnerships (H7) are connected to the self (H1). What you seek in a partner reflects who you are. Marriage transforms your identity. The partner mirrors your own qualities.'
    },
    8: {
        'title': 'Transformation — Through Courage',
        'description': 'Transformation and longevity (H8) are connected to courage and siblings (H3). Major changes come through brave actions. Siblings may go through transformative experiences.'
    },
    9: {
        'title': 'Dharma — Through Creativity',
        'description': 'Your dharma and fortune (H9) are connected to creativity and children (H5). Life purpose is expressed through creative work. Good fortune comes through children or students.'
    },
    10: {
        'title': 'Career — Through Partnerships',
        'description': 'Your career (H10) is connected to partnerships (H7). Professional success comes through collaborations. Business partnerships are key to career growth.'
    },
    11: {
        'title': 'Gains — Through Dharma',
        'description': 'Your gains and income (H11) are connected to dharma and fortune (H9). Wealth comes through righteous means, higher education, or foreign connections. Following your purpose brings financial rewards.'
    },
    12: {
        'title': 'Losses — Through Gains',
        'description': 'Your losses and expenses (H12) are connected to gains (H11). What you earn may be spent quickly. Foreign gains offset domestic losses. Spiritual spending (donations, retreats) is favorable.'
    },
}


def get_bhavat_bhavam(house: int) -> dict:
    """Get Bhavat Bhavam for a house."""
    bb_house = BHAVAT_BHAVAM.get(house, house)
    interp = INTERPRETATIONS.get(house, {})
    return {
        'house': house,
        'bhavat_bhavam_house': bb_house,
        'title': interp.get('title', ''),
        'description': interp.get('description', ''),
    }


def get_all_bhavat_bhavam() -> list[dict]:
    """Get Bhavat Bhavam for all 12 houses."""
    return [get_bhavat_bhavam(h) for h in range(1, 13)]


def get_planet_bhavat_bhavam(planets: dict, house_lords: dict) -> list[dict]:
    """Analyze Bhavat Bhavam with planet placements.

    Args:
        planets: dict of {name: PlanetPosition}
        house_lords: dict of {house: [planet_names]} — not used directly, derived from planets

    Returns:
        List of Bhavat Bhavam analyses with planetary info
    """
    results = []

    # Derive house lords from planets
    house_to_planets = {}
    for name, p in planets.items():
        house_to_planets.setdefault(p.house, []).append(name)

    for house in range(1, 13):
        bb = get_bhavat_bhavam(house)
        bb_house = bb['bhavat_bhavam_house']

        # What planets are in the BB house?
        planets_in_bb = house_to_planets.get(bb_house, [])

        # What planets are in the original house?
        planets_in_house = house_to_planets.get(house, [])

        results.append({
            'house': house,
            'bb_house': bb_house,
            'title': bb['title'],
            'planets_in_house': planets_in_house,
            'planets_in_bb_house': planets_in_bb,
        })

    return results
