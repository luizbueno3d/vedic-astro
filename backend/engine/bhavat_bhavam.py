"""Bhavat Bhavam — derivative house analysis.

Bhavat Bhavam means "the house of the house". In practice, a house is read not
only by its own natural meaning, but also by the same-numbered house counted from
itself.

Examples:
- H2 is further understood through the 2nd from H2 -> H3
- H5 is further understood through the 5th from H5 -> H9
- H8 is further understood through the 8th from H8 -> H3

This does not replace the original house. It shows the derived field through which
that house's results mature, reinforce themselves, or become more visible.
"""

HOUSE_NAMES = {
    1: 'self and identity',
    2: 'money, speech, and family resources',
    3: 'courage, skills, and initiative',
    4: 'home, mother, and emotional security',
    5: 'creativity, children, and intelligence',
    6: 'work, service, health, and conflict',
    7: 'relationships, partner, and public life',
    8: 'transformation, intimacy, and hidden processes',
    9: 'dharma, belief, teachers, and fortune',
    10: 'career, status, and visible karma',
    11: 'gains, networks, and long-term goals',
    12: 'loss, retreat, sleep, and liberation',
}

PLANET_THEMES = {
    'Sun': 'purpose, authority, and visibility',
    'Moon': 'emotional life and daily experience',
    'Mars': 'drive, courage, and force',
    'Mercury': 'thinking, speech, and analysis',
    'Jupiter': 'growth, guidance, and wisdom',
    'Venus': 'love, pleasure, and harmony',
    'Saturn': 'pressure, discipline, and long-term work',
    'Rahu': 'ambition, appetite, and worldly hunger',
    'Ketu': 'detachment, inner severance, and spiritual filtering',
}

PLANET_ACTIONS = {
    'Sun': 'build identity and direction',
    'Moon': 'seek emotional safety and belonging',
    'Mars': 'push, fight, and take initiative',
    'Mercury': 'think, connect, and interpret',
    'Jupiter': 'grow, teach, and make meaning',
    'Venus': 'bond, attract, and harmonize',
    'Saturn': 'work, endure, and mature slowly',
    'Rahu': 'chase, amplify, and intensify desire',
    'Ketu': 'detach, filter, and internalize',
}

HOUSE_CHANNELS = {
    1: 'through personal presence and direct self-expression',
    2: 'through money choices, speech, and value systems',
    3: 'through skills, courage, writing, and self-effort',
    4: 'through home life, roots, and inner emotional grounding',
    5: 'through creativity, romance, children, and intelligence',
    6: 'through work, discipline, conflict, healing, and service',
    7: 'through partners, clients, agreements, and public interaction',
    8: 'through crisis, transformation, research, and vulnerability',
    9: 'through teachers, belief, higher learning, and life philosophy',
    10: 'through career, public duty, visibility, and achievement',
    11: 'through networks, gains, allies, and future goals',
    12: 'through retreat, loss, foreignness, sleep, and spiritual distance',
}

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
        'description': 'The 1st from the 1st is again the 1st, so identity refers back to itself. This is the purest self-reference in the chart: body, personality, and direction are strengthened directly through self-awareness, self-effort, and personal presence.'
    },
    2: {
        'title': 'Wealth — Through Courage & Siblings',
        'description': 'The 2nd from the 2nd is the 3rd, so stored wealth is derived through effort, skill, initiative, communication, and enterprise. This is why H3 helps explain how H2 resources are built, used, and defended.'
    },
    3: {
        'title': 'Courage — Through Creativity & Children',
        'description': 'The 3rd from the 3rd is the 5th, so courage matures through intelligence, creativity, judgment, and inspired self-expression. H5 shows how skill becomes talent, and effort becomes something more refined and meaningful.'
    },
    4: {
        'title': 'Home — Through Partnerships',
        'description': 'The 4th from the 4th is the 7th, so inner security and domestic life are reflected through relationship, agreement, and public interaction. H7 shows how private foundations seek balance through another person or through external exchange.'
    },
    5: {
        'title': 'Creativity — Through Dharma & Fortune',
        'description': 'The 5th from the 5th is the 9th, so intelligence, children, and creativity are fulfilled through dharma, teachers, higher knowledge, and grace. H9 shows the higher meaning or destiny-pattern behind H5 matters.'
    },
    6: {
        'title': 'Enemies — Through Gains & Networks',
        'description': 'The 6th from the 6th is the 11th, so struggle, work, illness, and opposition are linked with gains, alliances, systems, and outcomes. H11 shows what comes out of disciplined 6th-house effort: improvement, results, and consequences.'
    },
    7: {
        'title': 'Partnerships — Through Self',
        'description': 'The 7th from the 7th is the 1st, so partnership ultimately reflects back to the self. H1 shows how relationships reshape identity, and why the partner often becomes a mirror of one’s own unfinished development.'
    },
    8: {
        'title': 'Transformation — Through Courage',
        'description': 'The 8th from the 8th is the 3rd, so crisis, transformation, secrets, and deep change push toward courage, initiative, skill, and effort. H3 shows the active response required when 8th-house processes demand movement.'
    },
    9: {
        'title': 'Dharma — Through Creativity',
        'description': 'The 9th from the 9th is the 5th, so dharma, wisdom, and blessing are carried through intelligence, creativity, students, and inspired expression. H5 shows how higher meaning becomes something personal and generative.'
    },
    10: {
        'title': 'Career — Through Partnerships',
        'description': 'The 10th from the 10th is the 7th, so status, profession, and public karma are strongly tied to relationship, contracts, clients, and visibility before others. H7 explains how career often becomes relational in its execution.'
    },
    11: {
        'title': 'Gains — Through Dharma',
        'description': 'The 11th from the 11th is the 9th, so gains, fulfillment, and networks are sustained by belief, ethics, blessings, teachers, and long-view purpose. H9 shows the higher principle that stabilizes H11 results.'
    },
    12: {
        'title': 'Losses — Through Gains',
        'description': 'The 12th from the 12th is the 11th, so loss, expenditure, retreat, and liberation are tied to gains, circles, and the fruits of one’s larger life network. H11 helps explain where 12th-house leakage, sacrifice, or release is feeding into a wider outcome.'
    },
}


def get_bhavat_bhavam(house: int) -> dict:
    """Get Bhavat Bhavam for a house."""
    bb_house = BHAVAT_BHAVAM.get(house, house)
    interp = INTERPRETATIONS.get(house, {})
    return {
        'house': house,
        'bhavat_bhavam_house': bb_house,
        'counting_rule': f'Take the {house}th house and count {house} houses from it. That lands in H{bb_house}.',
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


def get_planet_house_from_house_analysis(planets: dict) -> list[dict]:
    """Useful per-planet Bhavat Bhavam analysis.

    For each planet, read the natal house first, then the Bhavat Bhavam house of that
    natal house as the secondary support/output channel.
    """
    results = []
    for name, planet in planets.items():
        source_house = planet.house
        bb = get_bhavat_bhavam(source_house)
        derived_house = bb['bhavat_bhavam_house']

        source_topic = HOUSE_NAMES[source_house]
        derived_topic = HOUSE_NAMES[derived_house]
        planet_theme = PLANET_THEMES.get(name, name.lower())
        count_explanation = (
            f'Bhavat Bhavam uses derivative-house logic: take the {source_house}th house and count {source_house} houses from it. '
            f'Because {name} is in H{source_house}, that count lands in H{derived_house}, which becomes the derived house of manifestation for this placement.'
        )

        action = PLANET_ACTIONS.get(name, f'express {planet_theme}')
        summary = (
            f'{name} starts in H{source_house}, so the first story is {source_topic}. '
            f'{count_explanation} That is why H{derived_house} becomes the secondary field through which this placement tends to unfold {HOUSE_CHANNELS[derived_house]}.'
        )

        practical = (
            f'Practical reading: {name} will usually {action} first around H{source_house}, '
            f'but the result becomes more visible or complete when it moves into H{derived_house} themes. '
            f'That is why {source_topic} and {derived_topic} should be read together, not separately.'
        )

        results.append({
            'planet': name,
            'rashi': planet.rashi,
            'house': source_house,
            'bb_house': derived_house,
            'house_topic': source_topic,
            'bb_topic': derived_topic,
            'count_explanation': count_explanation,
            'summary': summary,
            'practical': practical,
        })

    return results
