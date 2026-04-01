"""Auto Reading — interpretive text generator.

Synthesizes all chart data into readable analysis.
"""

from .ephemeris import PlanetPosition, RASHI_LORDS, get_rashi_lord, NAKSHATRA_LORDS


def generate_reading(chart, dasha_data: dict, yogas: list, doshas: list,
                     shadbala: dict, ashtakavarga: dict,
                     house_rulerships: dict) -> dict:
    """Generate a full interpretive reading.

    Returns dict with sections: identity, strengths, challenges, career,
    relationships, health, spiritual, current_period, summary.
    """
    asc = chart.ascendant
    planets = chart.planets

    sections = {}

    # ===== IDENTITY =====
    sections['identity'] = _identity_section(asc, planets, house_rulerships)

    # ===== STRENGTHS =====
    sections['strengths'] = _strengths_section(planets, yogas, shadbala, ashtakavarga)

    # ===== CHALLENGES =====
    sections['challenges'] = _challenges_section(planets, doshas, ashtakavarga)

    # ===== CAREER =====
    sections['career'] = _career_section(planets, house_rulerships, yogas, shadbala)

    # ===== RELATIONSHIPS =====
    sections['relationships'] = _relationships_section(planets, house_rulerships)

    # ===== HEALTH =====
    sections['health'] = _health_section(planets, doshas, ashtakavarga)

    # ===== CURRENT PERIOD =====
    sections['current_period'] = _current_period_section(dasha_data, planets)

    # ===== SUMMARY =====
    sections['summary'] = _summary_section(sections, yogas, doshas, shadbala)

    return sections


def _identity_section(asc, planets, rulerships) -> str:
    moon = planets['Moon']
    sun = planets['Sun']

    # Ascendant description
    asc_descriptions = {
        'Aries': 'You lead with courage and initiative. Action-oriented, competitive, and pioneering.',
        'Taurus': 'You lead with stability and sensuality. Patient, reliable, and pleasure-seeking.',
        'Gemini': 'You lead with curiosity and communication. Versatile, witty, and adaptable.',
        'Cancer': 'You lead with feeling and protection. Nurturing, intuitive, and deeply emotional.',
        'Leo': 'You lead with confidence and creativity. Proud, generous, and naturally commanding.',
        'Virgo': 'You lead with precision and service. Analytical, practical, and perfectionist.',
        'Libra': 'You lead with balance and charm. Diplomatic, artistic, and partnership-oriented.',
        'Scorpio': 'You lead with intensity and depth. Transformative, secretive, and powerful.',
        'Sagittarius': 'You lead with vision and optimism. Philosophical, adventurous, and truth-seeking.',
        'Capricorn': 'You lead with discipline and ambition. Responsible, strategic, and enduring.',
        'Aquarius': 'You lead with innovation and independence. Humanitarian, unconventional, and future-focused.',
        'Pisces': 'You lead with intuition and compassion. Dreamy, artistic, and spiritually inclined.',
    }

    text = f"Your Ascendant is **{asc.rashi}** ({asc.nakshatra} Pada {asc.pada}). "
    text += asc_descriptions.get(asc.rashi, '') + "\n\n"

    text += f"Your Moon is in **{moon.rashi}** ({moon.nakshatra} Pada {moon.pada}) in H{moon.house}, "
    text += "which governs your emotional nature. "
    if moon.rashi_index == 7:  # Scorpio
        text += "Moon in Scorpio is debilitated — your emotions run deep and intense. You feel everything fully but may struggle with emotional vulnerability. "
    elif moon.rashi_index == 1:  # Taurus (exalted)
        text += "Moon in Taurus is exalted — you have deep emotional stability and a natural comfort with your feelings. "

    text += f"\n\nYour Sun is in **{sun.rashi}** in H{sun.house}, "
    text += "which represents your core identity and life purpose."

    return text


def _strengths_section(planets, yogas, shadbala, ashtakavarga) -> str:
    text = ""

    # Strongest planet
    if shadbala and shadbala.get('ranking'):
        strongest = shadbala['ranking'][0]
        text += f"Your strongest planet is **{strongest['planet']}** "
        p = shadbala['planets'].get(strongest['planet'], {})
        text += f"(score {strongest['score']:.3f}, {p.get('dignity', 'neutral')} in H{p.get('house', '?')}). "
        text += "This planet drives your life and amplifies whatever it touches.\n\n"

    # Yogas
    if yogas:
        for y in yogas:
            text += f"**{y.name}**: {y.description}\n\n"

    # Strong houses (Ashtakavarga)
    if ashtakavarga and ashtakavarga.get('house_scores'):
        strong_houses = [h for h, s in ashtakavarga['house_scores'].items() if s >= 5]
        if strong_houses:
            text += f"Houses with strong Ashtakavarga scores: H{', H'.join(str(h) for h in strong_houses)}. "
            text += "These areas of life flow more easily for you.\n\n"

    if not text:
        text = "Your chart shows balanced strength across planets."

    return text


def _challenges_section(planets, doshas, ashtakavarga) -> str:
    text = ""

    # Weak houses (Ashtakavarga)
    if ashtakavarga and ashtakavarga.get('house_scores'):
        weak_houses = [h for h, s in ashtakavarga['house_scores'].items() if s < 4]
        if weak_houses:
            text += f"Houses with weak Ashtakavarga scores: H{', H'.join(str(h) for h in weak_houses)}. "
            text += "These areas require more effort and attention.\n\n"

    # Doshas
    if doshas:
        for d in doshas:
            text += f"**{d.name}** ({d.severity}): {d.description}\n"
            if d.remedy:
                text += f"*Remedy: {d.remedy}*\n"
            text += "\n"

    # Debilitated planets
    for name, p in planets.items():
        if name in ('Rahu', 'Ketu'):
            continue
        # Simplified debilitation check
        deb = {'Sun': 6, 'Moon': 7, 'Mars': 3, 'Mercury': 11, 'Jupiter': 5, 'Venus': 8, 'Saturn': 0}
        if p.rashi_index == deb.get(name, -1):
            text += f"**{name} is debilitated** in {p.rashi} (H{p.house}) — "
            text += "this area of life requires extra effort and conscious development.\n\n"

    if not text:
        text = "No major challenges detected in your chart."

    return text


def _career_section(planets, rulerships, yogas, shadbala) -> str:
    text = ""

    # 10th house lord
    lord_10 = None
    for planet, houses in rulerships.items():
        if 10 in houses:
            lord_10 = planet
            break

    if lord_10 and lord_10 in planets:
        p = planets[lord_10]
        text += f"Your career is ruled by **{lord_10}** (10th lord), placed in H{p.house} ({p.rashi}). "
        text += f"This means your career is connected to the themes of the {p.rashi} sign and H{p.house}.\n\n"

    # Yogakaraka
    for y in yogas:
        if 'Yogakaraka' in y.name or 'Raja' in y.name:
            text += f"**{y.name}**: {y.description} — this supports career success.\n\n"

    # D10 chart themes
    text += "Career direction can be further analyzed through the D10 (Dashamamsha) chart.\n"

    return text


def _relationships_section(planets, rulerships) -> str:
    text = ""

    # 7th house lord
    lord_7 = None
    for planet, houses in rulerships.items():
        if 7 in houses:
            lord_7 = planet
            break

    if lord_7 and lord_7 in planets:
        p = planets[lord_7]
        text += f"Your partnerships are ruled by **{lord_7}** (7th lord), placed in H{p.house} ({p.rashi}). "

    # Venus as natural significator
    if 'Venus' in planets:
        v = planets['Venus']
        text += f"\n\nVenus (natural significator of love) is in {v.rashi} (H{v.house}). "
        if v.rashi_index == 9:  # Capricorn
            text += "Venus in Capricorn shows love expressed through loyalty, commitment, and practical support."

    # Moon for emotional connection
    moon = planets.get('Moon')
    if moon:
        text += f"\n\nYour emotional needs (Moon in {moon.rashi}) determine what you need from relationships."

    return text


def _health_section(planets, doshas, ashtakavarga) -> str:
    text = ""

    # 6th house
    if ashtakavarga and ashtakavarga.get('house_scores'):
        h6_score = ashtakavarga['house_scores'].get(6, 0)
        text += f"6th house (health) Ashtakavarga: {h6_score} bindus. "
        if h6_score < 4:
            text += "Health requires attention and proactive care.\n\n"
        else:
            text += "Health foundation is solid.\n\n"

    # Saturn-Mars conjunction
    if 'Mars' in planets and 'Saturn' in planets:
        if planets['Mars'].rashi_index == planets['Saturn'].rashi_index:
            text += "Saturn-Mars conjunction can indicate stress-related issues, "
            text += "particularly in the area of the body ruled by the house it sits in.\n\n"

    # Dosha health effects
    for d in doshas:
        if 'Kaal Sarpa' in d.name:
            text += "Kaal Sarpa Dosha can affect mental health — anxiety and sleep disturbances.\n\n"

    return text if text else "No specific health concerns indicated."


def _current_period_section(dasha_data, planets) -> str:
    text = ""
    current = dasha_data.get('current', {})

    if current.get('mahadasha'):
        md = current['mahadasha']
        text += f"**Current Mahadasha: {md['lord']}** ({md['start']} to {md['end']})\n\n"

    if current.get('antardasha'):
        ad = current['antardasha']
        text += f"**Current Antardasha: {ad['lord']}** ({ad['start']} to {ad['end']})\n\n"

    if current.get('pratyantardasha'):
        pd = current['pratyantardasha']
        text += f"**Current Pratyantardasha: {pd['lord']}** ({pd['start']} to {pd['end']})\n\n"

    if text:
        text += "The current period activates the houses ruled by these planets. "
        text += "Focus your energy on the areas of life connected to these lords."

    return text


def _summary_section(sections, yogas, doshas, shadbala) -> str:
    text = ""

    # Count strengths vs challenges
    strength_count = len(yogas)
    challenge_count = len(doshas)

    if shadbala and shadbala.get('ranking'):
        top = shadbala['ranking'][0]
        text += f"Your chart is driven by **{top['planet']}** — your most powerful planet.\n\n"

    if strength_count > 0:
        text += f"You have {strength_count} major yoga(s) supporting your growth and success.\n\n"

    if challenge_count > 0:
        text += f"You have {challenge_count} active dosha(s) to address with appropriate remedies.\n\n"

    text += "Remember: astrology shows potentials and tendencies, not fixed fate. "
    text += "Your awareness and choices shape how these energies manifest."

    return text
