"""Synthesis Engine — Cross-references all modules into coherent narrative.

This is the BRAIN of the app. It doesn't just display data — it CONNECTS
data points across modules to produce actual INSIGHTS.

Architecture:
1. Gather all data from every module
2. Cross-reference (e.g., Yogakaraka + Dasha + Transit = what?)
3. Prioritize (what matters most?)
4. Resolve contradictions (strong in D1 but weak in D9 = ?)
5. Generate coherent narrative
"""

from dataclasses import dataclass, field


@dataclass
class Insight:
    """A single synthesized insight."""
    category: str  # 'identity', 'career', 'relationship', 'health', 'timing', 'advice'
    priority: int  # 1=highest, 10=lowest
    title: str
    narrative: str
    supporting_data: list[str] = field(default_factory=list)


def synthesize(chart, house_rulerships: dict, yogas: list, doshas: list,
               shadbala: dict, ashtakavarga: dict, dasha_data: dict,
               transits: dict, vargas: dict, conjunctions: list,
               aspects: list, bhavat_bhavam: list) -> dict:
    """Master synthesis function. Returns structured analysis."""

    insights = []
    planets = chart.planets
    asc = chart.ascendant

    # ===== LAYER 1: IDENTITY =====
    insights.extend(_synthesize_identity(asc, planets, house_rulerships, shadbala))

    # ===== LAYER 2: STRENGTHS =====
    insights.extend(_synthesize_strengths(planets, yogas, shadbala, ashtakavarga, house_rulerships))

    # ===== LAYER 3: CHALLENGES =====
    insights.extend(_synthesize_challenges(planets, doshas, ashtakavarga, conjunctions))

    # ===== LAYER 4: CAREER =====
    insights.extend(_synthesize_career(planets, house_rulerships, yogas, shadbala, vargas, ashtakavarga))

    # ===== LAYER 5: RELATIONSHIPS =====
    insights.extend(_synthesize_relationships(planets, house_rulerships, vargas))

    # ===== LAYER 6: TIMING =====
    insights.extend(_synthesize_timing(dasha_data, transits, planets, ashtakavarga))

    # ===== LAYER 7: ACTIONABLE ADVICE =====
    insights.extend(_synthesize_advice(insights, dasha_data, doshas, yogas))

    # Sort by priority
    insights.sort(key=lambda x: x.priority)

    # Build sections
    sections = {}
    for cat in ['identity', 'strengths', 'challenges', 'career', 'relationships', 'timing', 'advice']:
        cat_insights = [i for i in insights if i.category == cat]
        if cat_insights:
            sections[cat] = cat_insights

    return {
        'insights': [vars(i) for i in insights],
        'sections': {k: [vars(i) for i in v] for k, v in sections.items()},
        'summary': _generate_summary(insights, shadbala, yogas, doshas, dasha_data),
        'key_themes': _extract_themes(insights, yogas, doshas),
    }


def _synthesize_identity(asc, planets, rulerships, shadbala) -> list[Insight]:
    """Who is this person? Core personality synthesis."""
    insights = []

    # Ascendant identity
    asc_identity = {
        'Cancer': ('You are a Nourisher — someone who leads by protecting, caring, and creating safety. Your emotional intelligence is your superpower, but it also means you absorb the energy of those around you.', 1),
        'Aries': ('You are a Pioneer — someone who leads through action and courage.', 1),
        'Leo': ('You are a Leader — someone who commands attention naturally.', 1),
        'Virgo': ('You are a Craftsman — someone who perfects through precision.', 1),
        'Scorpio': ('You are a Transformer — someone who sees beneath the surface.', 1),
        'Capricorn': ('You are a Builder — someone who creates through discipline.', 1),
    }
    identity_text, _ = asc_identity.get(asc.rashi, (f'Your {asc.rashi} Ascendant shapes how you present to the world.', 2))

    # Moon emotional nature
    moon = planets.get('Moon')
    if moon:
        if moon.rashi_index == 7:  # Scorpio (debilitated)
            identity_text += ' But your Moon is debilitated in Scorpio — your emotions run deeper and more intensely than most people. You feel everything fully. This is a gift for understanding others, but it can be exhausting for you.'
        elif moon.rashi_index == 1:  # Taurus (exalted)
            identity_text += ' Your exalted Moon in Taurus gives you deep emotional stability.'

    # Atmakaraka (highest degree planet)
    ak = max([(name, p.degree_in_sign) for name, p in planets.items()
              if name not in ('Rahu', 'Ketu')], key=lambda x: x[1])
    if ak[0] == 'Saturn':
        identity_text += f' Your Atmakaraka is Saturn — your soul\'s purpose is mastery through patience and discipline. You learn through time, not shortcuts.'

    insights.append(Insight('identity', 1, 'Core Identity', identity_text))

    return insights


def _synthesize_strengths(planets, yogas, shadbala, ashtakavarga, rulerships) -> list[Insight]:
    """What's powerful in this chart?"""
    insights = []

    # Strongest planet
    if shadbala and shadbala.get('ranking'):
        strongest = shadbala['ranking'][0]
        p = shadbala['planets'].get(strongest['planet'], {})
        houses_ruled = rulerships.get(strongest['planet'], [])

        text = f'Your most powerful planet is **{strongest["planet"]}** '
        text += f'(score {strongest["score"]:.3f}, {p.get("dignity", "neutral")} in H{p.get("house", "?")}). '
        text += f'It rules H{", H".join(str(h) for h in houses_ruled)} and sits in H{p.get("house", "?")}. '
        text += f'This means the themes of {strongest["planet"]} — '

        planet_themes = {
            'Sun': 'authority, self-expression, father, government',
            'Moon': 'emotions, mother, public, nurturing',
            'Mars': 'action, courage, competition, engineering',
            'Mercury': 'communication, business, analysis, writing',
            'Jupiter': 'wisdom, teaching, expansion, fortune',
            'Venus': 'beauty, relationships, arts, luxury',
            'Saturn': 'discipline, service, longevity, structure',
        }
        text += planet_themes.get(strongest['planet'], 'general significations') + ' — are your strongest areas.'

        insights.append(Insight('strengths', 2, f'{strongest["planet"]}: Your Power Planet', text))

    # Yogakaraka detection
    for planet, houses in rulerships.items():
        has_kendra = any(h in {1, 4, 7, 10} for h in houses)
        has_trikona = any(h in {1, 5, 9} for h in houses)
        if has_kendra and has_trikona and planet in planets:
            p = planets[planet]
            text = f'**{planet} is your Yogakaraka** — it rules both a Kendra (H{[h for h in houses if h in {1,4,7,10}]}) and a Trikona (H{[h for h in houses if h in {1,5,9}]}). '
            text += f'It sits in H{p.house} ({p.rashi}). '
            text += f'This is the single most important planet for success. Whatever house it sits in and aspects becomes a source of great achievement.'
            insights.append(Insight('strengths', 2, f'{planet}: Yogakaraka — Your Key to Success', text))

    # Strong houses (Ashtakavarga)
    if ashtakavarga and ashtakavarga.get('house_scores'):
        strong = [(h, s) for h, s in ashtakavarga['house_scores'].items() if s >= 5]
        if strong:
            text = 'Houses with strong Ashtakavarga scores flow more easily for you: '
            text += ', '.join(f'H{h} ({s} bindus)' for h, s in strong)
            text += '. These areas of life require less effort and produce more results.'
            insights.append(Insight('strengths', 4, 'Strong Houses (Ashtakavarga)', text))

    # Key yogas
    for y in yogas:
        if 'Raja' in y.name or 'Yogakaraka' in y.name:
            text = f'{y.description}. This yoga supports authority, success, and recognition.'
            insights.append(Insight('strengths', 3, y.name, text))
        elif 'Viparita' in y.name:
            text = f'{y.description}. This unusual yoga means your greatest successes come from unexpected places — through losses, setbacks, or unconventional paths.'
            insights.append(Insight('strengths', 4, y.name, text))

    return insights


def _synthesize_challenges(planets, doshas, ashtakavarga, conjunctions) -> list[Insight]:
    """What's difficult in this chart?"""
    insights = []

    # Debilitated planets
    deb = {'Sun': 6, 'Moon': 7, 'Mars': 3, 'Mercury': 11, 'Jupiter': 5, 'Venus': 8, 'Saturn': 0}
    for name, p in planets.items():
        if name in deb and p.rashi_index == deb[name]:
            text = f'{name} is debilitated in {p.rashi} (H{p.house}). '
            themes = {
                'Moon': 'Your emotional foundation is intense but unstable. You need to consciously build emotional resilience.',
                'Sun': 'Authority and self-expression may feel difficult. You may struggle with confidence or relationship with father.',
                'Mars': 'Energy and courage need to be channeled carefully. Aggression or passivity extremes.',
                'Mercury': 'Communication and business sense need development. Overthinking or underthinking.',
                'Jupiter': 'Wisdom and fortune require extra effort. Teachers and mentors are especially important.',
                'Venus': 'Relationships and creativity face challenges. You may undervalue yourself or overvalue others.',
                'Saturn': 'Discipline and structure feel heavy. Career may take longer to establish.',
            }
            text += themes.get(name, 'This area requires extra attention.')
            insights.append(Insight('challenges', 3, f'{name} Debilitated in H{p.house}', text))

    # Weak houses (Ashtakavarga)
    if ashtakavarga and ashtakavarga.get('house_scores'):
        weak = [(h, s) for h, s in ashtakavarga['house_scores'].items() if s < 4]
        if weak:
            text = 'Houses with weak Ashtakavarga require more effort: '
            text += ', '.join(f'H{h} ({s} bindus)' for h, s in weak)
            text += '. Focus energy here proactively rather than reactively.'
            insights.append(Insight('challenges', 5, 'Weak Houses Need Attention', text))

    # Doshas
    for d in doshas:
        text = f'{d.description}'
        if d.remedy:
            text += f' **Remedy:** {d.remedy}'
        insights.append(Insight('challenges', 3 if d.severity == 'high' else 5, d.name, text))

    return insights


def _synthesize_career(planets, rulerships, yogas, shadbala, vargas, ashtakavarga) -> list[Insight]:
    """Career and professional direction synthesis."""
    insights = []

    # 10th lord analysis
    lord_10 = None
    for planet, houses in rulerships.items():
        if 10 in houses:
            lord_10 = planet
            break

    if lord_10 and lord_10 in planets:
        p = planets[lord_10]

        # Also check what other houses the 10th lord rules
        other_houses = [h for h in rulerships[lord_10] if h != 10]

        text = f'Your career is ruled by **{lord_10}**, placed in H{p.house} ({p.rashi}, {p.nakshatra}). '

        # What does the placement mean?
        house_meanings = {
            1: 'Your career is deeply personal — you ARE your work. Self-employment or leadership roles suit you.',
            2: 'Career connected to wealth, family business, speech, or food industry.',
            3: 'Career through communication, skills, writing, media, or younger generation.',
            4: 'Career connected to home, real estate, vehicles, mother, or comfort.',
            5: 'Career through creativity, children, education, speculation, or entertainment.',
            6: 'Career in service, health, law, or defeating competitors. Daily routine matters.',
            7: 'Career through partnerships, foreign connections, or dealing with the public.',
            8: 'Career in research, transformation, insurance, occult, or crisis management.',
            9: 'Career connected to dharma, teaching, law, religion, foreign lands, or publishing.',
            10: 'Strong career placement — natural authority and recognition in profession.',
            11: 'Career through networks, elder siblings, large organizations, or income management.',
            12: 'Career in foreign lands, hospitals, prisons, ashrams, or behind-the-scenes work.',
        }
        text += house_meanings.get(p.house, '')

        if other_houses:
            text += f' Also rules H{", H".join(str(h) for h in other_houses)} — career connects to those life areas too.'

        insights.append(Insight('career', 2, f'Career Direction: {lord_10} in H{p.house}', text))

    # D10 chart career confirmation
    if vargas and 'D10' in vargas:
        d10 = vargas['D10']['signs']
        d10_asc = d10.get('Asc', '?')
        text = f'Your D10 (career chart) Ascendant is **{d10_asc}**. '
        d10_interps = {
            'Leo': 'Natural leader in career. Authority, creativity, and recognition are themes.',
            'Virgo': 'Analytical, service-oriented career. Detail work, health, or craft.',
            'Scorpio': 'Research, transformation, crisis management, or investigation.',
            'Capricorn': 'Business, government, long-term career building. Late success.',
            'Aquarius': 'Technology, innovation, social causes, unconventional career.',
            'Pisces': 'Creative, spiritual, healing, or foreign-connected career.',
        }
        text += d10_interps.get(d10_asc, '')
        insights.append(Insight('career', 3, f'D10 Career Chart: {d10_asc} Rising', text))

    return insights


def _synthesize_relationships(planets, rulerships, vargas) -> list[Insight]:
    """Relationship and marriage synthesis."""
    insights = []

    # 7th lord
    lord_7 = None
    for planet, houses in rulerships.items():
        if 7 in houses:
            lord_7 = planet
            break

    if lord_7 and lord_7 in planets:
        p = planets[lord_7]
        text = f'Your partnerships are ruled by **{lord_7}**, in H{p.house} ({p.rashi}). '

        house_rel_meanings = {
            1: 'Partner mirrors your own qualities. Marriage transforms your identity.',
            2: 'Partner brings wealth or comes from wealthy family. Family plays role in marriage.',
            3: 'Partner may be a communicator, writer, or from sibling\'s circle.',
            4: 'Partner connected to home or mother. Domestic happiness through marriage.',
            5: 'Romantic marriage. Partner may be creative or from educational setting.',
            6: 'Marriage requires work. Partner may be in service or health field.',
            7: 'Strong partnership placement. Partner is significant and prominent.',
            8: 'Transformative marriage. Deep, intense, possibly secretive relationship.',
            9: 'Partner from different background or foreign. Fortunate marriage.',
            10: 'Partner connected to career or public life. Professional partnership.',
            11: 'Partner from social network. Marriage brings gains.',
            12: 'Foreign partner or marriage involving travel. Spiritual connection.',
        }
        text += house_rel_meanings.get(p.house, '')
        insights.append(Insight('relationships', 3, f'Partnership: {lord_7} in H{p.house}', text))

    # Venus as natural significator
    if 'Venus' in planets:
        v = planets['Venus']
        text = f'Venus (love significator) is in {v.rashi} (H{v.house}). '
        venus_signs = {
            'Capricorn': 'You express love through loyalty, commitment, and practical support. You show love by being dependable, not by grand gestures.',
            'Taurus': 'Sensual, steady love. You value comfort and loyalty in relationships.',
            'Libra': 'Charming, balanced partnerships. You seek equality and beauty.',
            'Pisces': 'Romantic, idealistic love. You may idealize partners.',
            'Virgo': 'Love expressed through service and attention to detail. Critical of partners.',
            'Scorpio': 'Intense, possessive love. Deep bonds but jealousy issues.',
        }
        text += venus_signs.get(v.rashi, '')
        insights.append(Insight('relationships', 4, f'Venus in {v.rashi}: How You Love', text))

    return insights


def _synthesize_timing(dasha_data, transits, planets, ashtakavarga) -> list[Insight]:
    """What's happening NOW and what's coming."""
    insights = []
    current = dasha_data.get('current', {})

    if current.get('mahadasha'):
        md = current['mahadasha']
        ad = current.get('antardasha', {})
        pd = current.get('pratyantardasha', {})

        md_lord = md['lord']
        ad_lord = ad.get('lord', '?')
        pd_lord = pd.get('lord', '?')

        text = f'You are in **{md_lord} Mahadasha** ({"%.0f" % md.get("years", 0)} years, {md["start"]} to {md["end"]}). '
        text += f'Current sub-period: {ad_lord} Antardasha, {pd_lord} Pratyantardasha. '

        # What does the MD lord activate?
        md_themes = {
            'Venus': 'This 20-year period focuses on relationships, comfort, arts, luxury, and gains through networks.',
            'Jupiter': 'Expansion, wisdom, teaching, fortune, and spiritual growth.',
            'Saturn': 'Discipline, hard work, delays but lasting results, service.',
            'Mars': 'Action, energy, competition, property, courage.',
            'Mercury': 'Communication, business, analysis, writing, learning.',
            'Sun': 'Authority, self-expression, government, father.',
            'Moon': 'Emotions, public, mother, changes, nurturing.',
            'Rahu': 'Unconventional, foreign, obsession, sudden changes.',
            'Ketu': 'Spiritual, detachment, past life karma, research.',
        }
        text += md_themes.get(md_lord, '')

        # Remaining time
        from datetime import date
        end = date.fromisoformat(md['end'])
        remaining = (end - date.today()).days
        text += f' **{remaining} days ({remaining/365.25:.1f} years) remaining** in this Mahadasha.'

        insights.append(Insight('timing', 1, f'Current Period: {md_lord} MD → {ad_lord} AD → {pd_lord} PD', text))

    # Key transits
    if transits:
        for name, t in transits.items():
            if name in ('Jupiter', 'Saturn') and abs(t.get('orb', 0)) < 5:
                text = f'{name} is transiting H{t["house"]} ({t["rashi"]}), just {abs(t["orb"]):.1f}° from natal position. '
                text += 'This is a significant activation period.'
                insights.append(Insight('timing', 3, f'{name} Transit Activation', text))

    return insights


def _synthesize_advice(insights, dasha_data, doshas, yogas) -> list[Insight]:
    """Actionable advice based on synthesis."""
    insights_out = []

    # General advice based on what was found
    challenge_count = len([i for i in insights if i.category == 'challenges'])
    strength_count = len([i for i in insights if i.category == 'strengths'])

    if strength_count > challenge_count:
        text = 'Your chart has more strengths than challenges. Focus on amplifying your strong planets and houses rather than fixing weaknesses.'
    elif challenge_count > strength_count:
        text = 'Your chart shows significant challenges. Prioritize remedies for the most impactful doshas and debilitated planets.'
    else:
        text = 'Your chart is balanced between strengths and challenges. The key is TIMING — knowing when to push and when to wait.'

    insights_out.append(Insight('advice', 5, 'Strategic Approach', text))

    # Dasha-specific advice
    current = dasha_data.get('current', {})
    if current.get('antardasha'):
        ad_lord = current['antardasha']['lord']
        ad_themes = {
            'Jupiter': 'This is a period for learning, teaching, expansion, and seeking wisdom. Say yes to opportunities involving growth.',
            'Saturn': 'Discipline and patience are required now. Don\'t force things. Build slowly and deliberately.',
            'Venus': 'Focus on relationships, arts, comfort, and financial planning. A good time for partnerships.',
            'Mars': 'Take action, start projects, compete. But avoid impulsiveness.',
            'Mercury': 'Communication, business deals, writing, and analysis are favored.',
            'Sun': 'Step into leadership. Express yourself. Deal with authority figures.',
            'Moon': 'Public-facing activities, nurturing, and emotional work are favored.',
        }
        if ad_lord in ad_themes:
            insights_out.append(Insight('advice', 4, f'What to Do During {ad_lord} AD', ad_themes[ad_lord]))

    return insights_out


def _generate_summary(insights, shadbala, yogas, doshas, dasha_data) -> str:
    """Generate a concise summary of the entire chart."""
    parts = []

    if shadbala and shadbala.get('ranking'):
        top = shadbala['ranking'][0]
        parts.append(f'Your chart is driven by **{top["planet"]}** (strongest planet).')

    if yogas:
        parts.append(f'{len(yogas)} major yoga(s) found, including: {", ".join(y.name for y in yogas[:3])}.')

    if doshas:
        parts.append(f'{len(doshas)} active dosha(s) to address.')
    else:
        parts.append('No major doshas — chart is clean.')

    current = dasha_data.get('current', {})
    if current.get('mahadasha'):
        parts.append(f'Currently in {current["mahadasha"]["lord"]} MD, {current.get("antardasha", {}).get("lord", "?")} AD.')

    return ' '.join(parts)


def _extract_themes(insights, yogas, doshas) -> list[str]:
    """Extract key themes from the analysis."""
    themes = set()

    for i in insights:
        if 'career' in i.category or 'Yogakaraka' in i.title:
            themes.add('Career & Purpose')
        if 'relationship' in i.category or 'Venus' in i.title:
            themes.add('Love & Relationships')
        if 'debilitated' in i.title.lower():
            themes.add('Emotional Depth')
        if 'Viparita' in i.title:
            themes.add('Success Through Adversity')
        if 'timing' in i.category:
            themes.add('Timing & Cycles')

    for y in yogas:
        if 'Raja' in y.name:
            themes.add('Authority & Success')
        if 'Budhaditya' in y.name:
            themes.add('Intelligence & Communication')

    return list(themes)
