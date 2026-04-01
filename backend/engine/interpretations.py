"""Pre-computed interpretations — Honest + Empowering + Magical.

Three-part arc for every placement:
1. REALITY — what this actually means (honest, no sugarcoating)
2. HOW TO HANDLE IT — practical advice, what to do
3. THE MAGIC — when mastered, what becomes possible

Never exaggerate. Always grounded. Always end with possibility.
"""

# Nakshatra interpretations — focus on the GIFT of each
NAKSHATRA_INTERPS = {
    'Ashwini': {'gift': 'Natural healer and pioneer — you start things others can\'t', 'deity': 'Ashwini Kumaras', 'quality': 'Initiator'},
    'Bharani': {'gift': 'Ability to transform and endure what breaks others', 'deity': 'Yama', 'quality': 'Transformer'},
    'Krittika': {'gift': 'Sharp clarity — you see through confusion to the truth', 'deity': 'Agni', 'quality': 'Purifier'},
    'Rohini': {'gift': 'Natural magnetism — beauty and abundance flow through you', 'deity': 'Brahma', 'quality': 'Creator'},
    'Mrigashira': {'gift': 'Curiosity that leads to discovery — the eternal seeker finds gold', 'deity': 'Soma', 'quality': 'Seeker'},
    'Ardra': {'gift': 'Power to destroy what\'s broken and rebuild stronger', 'deity': 'Rudra', 'quality': 'Destroyer-rebuilder'},
    'Punarvasu': {'gift': 'Infinite renewal — you always bounce back, stronger each time', 'deity': 'Aditi', 'quality': 'Renewer'},
    'Pushya': {'gift': 'Natural nurturer — you make others feel safe and nourished', 'deity': 'Brihaspati', 'quality': 'Nourisher'},
    'Ashlesha': {'gift': 'Penetrating insight — you understand what others can\'t see', 'deity': 'Nagas', 'quality': 'Seer'},
    'Magha': {'gift': 'Natural authority — legacy and tradition flow through you', 'deity': 'Pitris', 'quality': 'Royal'},
    'P.Phalguni': {'gift': 'Joy of creation — you bring pleasure and beauty to life', 'deity': 'Bhaga', 'quality': 'Joy-bringer'},
    'U.Phalguni': {'gift': 'Natural partner — you build things together with others', 'deity': 'Aryaman', 'quality': 'Partner'},
    'Hasta': {'gift': 'Skilled hands — what you build with your hands has power', 'deity': 'Savitar', 'quality': 'Craftsman'},
    'Chitra': {'gift': 'Architect of beauty — you design things that inspire', 'deity': 'Vishvakarma', 'quality': 'Architect'},
    'Swati': {'gift': 'Independent spirit — you move with the wind and land on your feet', 'deity': 'Vayu', 'quality': 'Independent'},
    'Vishakha': {'gift': 'Unstoppable determination — once you choose a goal, you reach it', 'deity': 'Indra-Agni', 'quality': 'Determined'},
    'Anuradha': {'gift': 'Deep devotion — your loyalty and discipline create lasting bonds', 'deity': 'Mitra', 'quality': 'Devotee'},
    'Jyeshtha': {'gift': 'Protective power — you shield those you love with quiet strength', 'deity': 'Indra', 'quality': 'Protector'},
    'Mula': {'gift': 'Root-finder — you go to the foundation of any truth', 'deity': 'Nirriti', 'quality': 'Root-searcher'},
    'P.Ashadha': {'gift': 'Invincibility through purification — what doesn\'t break you makes you unbreakable', 'deity': 'Apas', 'quality': 'Invincible'},
    'U.Ashadha': {'gift': 'Universal victory — your success lifts others too', 'deity': 'Vishvadevas', 'quality': 'Universal'},
    'Sravana': {'gift': 'Deep listening — you hear what others miss, and learn from everything', 'deity': 'Vishnu', 'quality': 'Listener'},
    'Dhanishtha': {'gift': 'Symphony of talents — multiple skills create extraordinary results', 'deity': 'Vasus', 'quality': 'Multi-talented'},
    'Shatabhisha': {'gift': 'Healer through knowledge — your research cures what others can\'t', 'deity': 'Varuna', 'quality': 'Healer'},
    'P.Bhadrapada': {'gift': 'Transformation through intensity — you go deep and come back wiser', 'deity': 'Aja Ekapada', 'quality': 'Deep transformer'},
    'U.Bhadrapada': {'gift': 'Wisdom from the depths — your understanding comes from experience, not books', 'deity': 'Ahir Budhnya', 'quality': 'Deep wise one'},
    'Revati': {'gift': 'Completion energy — you finish what others abandon, and find peace at the end', 'deity': 'Pushan', 'quality': 'Completer'},
}

# Pada rulers
PADA_RULERS_SEQUENCE = ['Mars', 'Venus', 'Mercury', 'Moon']


def interpret_full(name: str, rashi: str, house: int, nakshatra: str, pada: int,
                   retrograde: bool, houses_ruled: list[int], dignity: str,
                   in_d9: str = None, varga_d10: str = None) -> str:
    """Three-part arc: Reality → How to handle → The magic."""

    parts = []

    # === PART 1: REALITY ===
    nak = NAKSHATRA_INTERPS.get(nakshatra, {})
    retro = " Retrograde — this energy turns inward." if retrograde else ""

    reality = f"{name} in {rashi}, House {house}.{retro}"
    if nak:
        reality += f" Nakshatra: {nakshatra} — {nak.get('gift', '')}."
    if dignity and dignity != 'neutral':
        reality += _dignity_reality(name, dignity, rashi)

    parts.append(f"REALITY: {reality}")

    # === PART 2: HOW TO HANDLE ===
    advice = _how_to_handle(name, house, dignity, retrograde, houses_ruled)
    if advice:
        parts.append(f"HOW TO HANDLE: {advice}")

    # === PART 3: THE MAGIC ===
    magic = _the_magic(name, house, dignity, houses_ruled, nak, in_d9, varga_d10)
    if magic:
        parts.append(f"THE MAGIC: {magic}")

    return "\n".join(parts)


def _dignity_reality(planet: str, dignity: str, rashi: str) -> str:
    """Honest assessment of dignity."""
    if dignity == 'exalted':
        return f" Exalted in {rashi} — this planet operates at maximum power."
    elif dignity == 'own_sign':
        return f" In own sign {rashi} — fully at home, expressing authentically."
    elif dignity == 'debilitated':
        return _debilitation_reality(planet, rashi)
    else:
        return ""


def _debilitation_reality(planet: str, rashi: str) -> str:
    """Honest debilitation assessment — no sugarcoating, but no doom either."""
    reals = {
        'Moon': f" Debilitated in {rashi}. Your emotional engine runs on intensity rather than comfort. You feel everything deeply — sometimes too deeply. Emotional overwhelm is real for you.",
        'Sun': f" Debilitated in {rashi}. Authority and self-expression don't come naturally. You may struggle with confidence or have a complicated relationship with father/authority figures.",
        'Mars': f" Debilitated in {rashi}. Energy and courage need careful channeling. You may swing between aggression and passivity.",
        'Mercury': f" Debilitated in {rashi}. Communication and analysis can be a challenge. You may overthink or underthink.",
        'Jupiter': f" Debilitated in {rashi}. Wisdom and fortune require extra effort. Teachers and mentors are especially important for you.",
        'Venus': f" Debilitated in {rashi}. Relationships and creativity face challenges. You may undervalue yourself or overvalue others.",
        'Saturn': f" Debilitated in {rashi}. Discipline and structure feel heavy. Career may take longer to establish, but when it does, it's built on solid ground.",
    }
    return reals.get(planet, f" Debilitated in {rashi}.")


def _how_to_handle(planet: str, house: int, dignity: str, retrograde: bool,
                   houses_ruled: list[int]) -> str:
    """Practical advice for this placement."""
    advice = []

    # Dignity-specific advice
    if dignity == 'debilitated':
        deb_remedies = {
            'Moon': 'Channel the intensity: meditation, creative writing, psychology, working with water. Create a daily emotional practice — journaling, breathwork, or simply sitting with your feelings for 10 minutes each morning.',
            'Sun': 'Build confidence through small wins. Take on leadership in low-stakes environments first. Address father wounds consciously — therapy or honest conversations.',
            'Mars': 'Physical exercise is NON-NEGOTIABLE. Martial arts, running, anything that channels aggression constructively. Choose your battles — not every fight is yours.',
            'Mercury': 'Write every day. Even 10 minutes. Writing trains the mind that Mercury debilitates. Also: learn one thing deeply rather than many things superficially.',
            'Jupiter': 'Seek teachers. Read philosophy. Study something that connects you to wisdom traditions. Give generously — Jupiter strengthens through giving.',
            'Venus': 'Create beauty in your daily life. Cook well, dress intentionally, cultivate one artistic skill. In relationships: learn to receive, not just give.',
            'Saturn': 'Build routines. Start small and be consistent. Saturn rewards patience, not intensity. One year of daily practice beats one month of 12-hour days.',
        }
        advice.append(deb_remedies.get(planet, 'Develop this energy consciously.'))

    # Retrograde advice
    if retrograde:
        advice.append(f"For retrograde {planet}: Give yourself permission to process internally before acting. Your timing is different from others — and that\'s fine. The work you do in private creates mastery in public.")

    # House-specific advice
    house_advice = {
        3: 'Your skills are your superpower. Invest in hands-on learning. Communication, writing, technical skills — these are your currency.',
        5: 'Creativity isn\'t optional for you — it\'s how you process life. Find your medium: music, writing, art, teaching, parenting.',
        8: 'Research and transformation are your territory. Don\'t fear depth — you\'re built for it. Psychology, occult, healing, crisis management — these are your strengths.',
        9: 'Higher learning opens doors. Seek mentors, study philosophy, travel if possible. Your fortune comes through dharma.',
        10: 'Your career is central to your identity. Take it seriously. Build something lasting.',
        12: 'Solitude and spirituality aren\'t escapes — they\'re how you recharge. Foreign connections and behind-the-scenes work suit you.',
    }
    if house in house_advice:
        advice.append(house_advice[house])

    return " ".join(advice)


def _the_magic(planet: str, house: int, dignity: str, houses_ruled: list[int],
               nak: dict, in_d9: str = None, varga_d10: str = None) -> str:
    """The transformative possibility — what happens when you do the work."""
    magic = []

    # Dignity magic
    if dignity == 'debilitated':
        deb_magic = {
            'Moon': 'And here\'s the magic: when you MASTER this intensity — and you can — you become someone who understands the human heart at a level most people never reach. Scorpio Moon people who do the work become the most profound healers, artists, and leaders. You\'ve been to the depths. That\'s your gift.',
            'Sun': 'When you find your authentic voice — not the one others expect, but YOURS — it carries extraordinary weight. Debilitated Sun people who stop trying to be "normal" leaders often become the most innovative ones.',
            'Mars': 'When you channel this energy through a skill rather than raw aggression, you become unstoppable. The debilitation forces you to be STRATEGIC rather than impulsive — and strategic Mars wins every time.',
            'Mercury': 'When Mercury is debilitated but you develop it through practice (writing, speaking, analyzing), you often become DEEPER than naturally gifted communicators. You understand the weight of words.',
            'Jupiter': 'When you earn your wisdom through experience rather than receiving it easily, it\'s more valuable. Debilitated Jupiter people who seek teachers often become the best teachers themselves.',
            'Venus': 'When you learn to love consciously rather than effortlessly, your love is CHOSEN — and chosen love is the strongest kind. You appreciate beauty because you know what it\'s like without it.',
            'Saturn': 'What Saturn delays, Saturn makes LASTING. The career that takes longer to build stands longer. The discipline you develop through struggle becomes unshakeable.',
        }
        magic.append(deb_magic.get(planet, ''))

    # Yogakaraka magic
    if 5 in houses_ruled and 10 in houses_ruled:
        magic.append(f"{planet} is your Yogakaraka — the planet that combines career (H10) and creativity (H5). When you combine what you love with what you do professionally, everything accelerates. This is your shortcut to success: make your work creative and your creativity work.")

    # D9 confirmation magic
    if in_d9 and 'own' in in_d9.lower() or (in_d9 and 'Taurus' in in_d9 and planet == 'Venus'):
        magic.append(f"And confirmed in the D9 (inner chart): {planet} in {in_d9}. This means your INNER nature supports this energy. What looks like a surface challenge hides a deep strength.")

    return " ".join(magic)


def interpret_conjunction(planet1: str, planet2: str, house: int, sign: str, orb: float) -> str:
    """Three-part conjunction interpretation."""
    combos = {
        ('Mars', 'Saturn'): (
            "Reality: Mars and Saturn are conjunct — drive meets discipline. These energies pull in opposite directions: Mars wants to rush, Saturn wants to wait.",
            "How to handle: Use Mars for energy and Saturn for precision. Let Mars start the engine, Saturn steer the wheel. Don't fight the tension — USE it.",
            "The magic: This is the warrior-monk signature. People with this conjunction who learn to balance action and patience develop technical mastery that purely Mars or purely Saturn people can't match. You can work on something for YEARS without losing focus."
        ),
        ('Sun', 'Mercury'): (
            "Reality: Sun-Mercury conjunction — intelligence fused with self-expression.",
            "How to handle: Write, speak, teach. Your mind wants to communicate.",
            "The magic: When your thinking and identity are this connected, you speak your truth with unusual clarity. Others hear AND believe you."
        ),
    }

    key = tuple(sorted([planet1, planet2]))
    tight = "deeply fused" if orb < 3 else "strongly connected" if orb < 6 else "connected"

    if key in combos:
        reality, howto, magic = combos[key]
        return f"{reality} [{tight}]\n{howto}\n{magic}"
    else:
        return f"{planet1}-{planet2} conjunction in H{house} ({sign}) — these energies combine in your life [{tight}]"


def interpret_planet(name: str, rashi: str, rashi_index: int, house: int,
                     nakshatra: str, pada: int, retrograde: bool,
                     houses_ruled: list[int], dignity: str,
                     in_d9: str = None) -> str:
    """Generate EMPOWERING interpretation for a planet."""

    lines = []

    # Nakshatra GIFT (lead with this)
    nak = NAKSHATRA_INTERPS.get(nakshatra, {})
    if nak:
        lines.append(f"Gift: {nak.get('gift', '')}")

    # Dignity — frame as opportunity, not limitation
    dignity_frames = {
        'exalted': 'Operating at peak power — this energy flows naturally for you',
        'own_sign': 'Fully at home — this planet expresses itself authentically through you',
        'moolatrikona': 'Near peak power — strong foundation for this energy',
        'debilitated': 'This energy is INTENSE rather than weak — it demands conscious development, but when mastered, creates depth others can\'t reach',
        'neutral': 'Balanced expression — you can shape this energy however you choose',
    }
    if dignity:
        lines.append(dignity_frames.get(dignity, ''))

    # Houses ruled — what this planet GIVES you
    if houses_ruled:
        house_gifts = {
            1: 'your identity and presence', 2: 'your wealth and voice', 3: 'your courage and skills',
            4: 'your home and emotional foundation', 5: 'your creativity and joy', 6: 'your ability to serve and heal',
            7: 'your partnerships', 8: 'your transformative power', 9: 'your fortune and wisdom',
            10: 'your career and legacy', 11: 'your gains and network', 12: 'your spiritual depth',
        }
        gifts = [house_gifts.get(h, f'H{h}') for h in houses_ruled]
        lines.append(f"This planet gives you: {', '.join(gifts)}")

    # Retrograde — frame as internalized strength
    if retrograde:
        lines.append(f"Retrograde: This energy works DEEPLY and INTERNALLY — you process it before expressing it, which creates mastery through reflection")

    # Pada ruler
    pada_ruler = PADA_RULERS_SEQUENCE[(pada - 1) % 4] if pada else ''
    lines.append(f"Pada {pada} ({pada_ruler}-influenced)")

    # D9 confirmation
    if in_d9:
        lines.append(f"Inner nature (D9): {in_d9}")

    return " | ".join(lines)


def interpret_conjunction(planet1: str, planet2: str, house: int, sign: str, orb: float) -> str:
    """Frame conjunctions as SYNERGIES, not problems."""
    combos = {
        ('Mars', 'Saturn'): 'The warrior-monk — you have BOTH drive AND patience. This rare combination creates technical mastery that others can\'t match. When Mars wants to rush, Saturn slows you down to get it RIGHT. When Saturn wants to delay forever, Mars pushes you to act.',
        ('Sun', 'Mercury'): 'The brilliant communicator — intelligence and self-expression fused. You think AND speak clearly.',
        ('Moon', 'Jupiter'): 'Emotional wisdom — you feel deeply AND understand broadly. Natural teacher-healer energy.',
        ('Moon', 'Mars'): 'Emotional courage — you act on your feelings with conviction. Financial boldness.',
        ('Venus', 'Saturn'): 'Love with loyalty — your relationships are built to LAST. You don\'t love casually, and that\'s a strength.',
        ('Jupiter', 'Saturn'): 'The wise builder — you plan for the long term with both optimism and realism.',
    }

    key = tuple(sorted([planet1, planet2]))
    interp = combos.get(key, f'{planet1}-{planet2} fusion — these energies work together in your life')

    tight = "deeply fused" if orb < 3 else "strongly connected" if orb < 6 else "connected"
    return f"{interp} [{tight}, orb {orb:.1f}°]"


def interpret_yoga(name: str, planets: list, description: str, strength: str) -> str:
    """Frame yogas as SUPERPOWERS."""
    yoga_gifts = {
        'Raja Yoga': 'Authority and success — you have the planetary combination for recognition and power',
        'Yogakaraka Raja Yoga': 'Exceptional success formula — your Yogakaraka creates a direct path to achievement',
        'Dhana Yoga': 'Wealth magnet — your planets are wired for financial abundance',
        'Vimala Viparita Raja Yoga': 'The phoenix — your greatest successes come from unexpected places. Losses transform into gains.',
        'Harsha Viparita Raja Yoga': 'Triumph through challenge — obstacles become your stepping stones',
        'Sarala Viparita Raja Yoga': 'Fearlessness under pressure — you thrive in crisis when others panic',
        'Budhaditya Yoga': 'Sharp mind — intelligence and communication are your superpowers',
        'Gaja Kesari Yoga': 'The wise elephant — wisdom, prosperity, and respect flow to you naturally',
        'Hamsa Yoga': 'Spiritual wisdom — your Jupiter gives you access to higher knowledge',
        'Malavya Yoga': 'Beauty and charm — aesthetic sense and attraction are natural gifts',
        'Ruchaka Yoga': 'Courage and leadership — Mars gives you the drive to lead',
        'Shasha Yoga': 'Discipline mastery — Saturn gives you the patience others lack',
        'Bhadra Yoga': 'Communication genius — Mercury makes you a natural writer/speaker',
        'Neechabhanga Raja Yoga': 'The alchemist — your weakness becomes your greatest strength when transformed',
        'Chandra Mangala Yoga': 'Bold action — you act on instinct with financial intelligence',
    }

    base = yoga_gifts.get(name, name)
    return f"{base}. {description}"


def interpret_dosha(name: str, severity: str, description: str, remedy: str) -> str:
    """Frame doshas as GROWTH AREAS, not curses."""
    frames = {
        'Mangal Dosha': 'Intense Mars energy in relationships — you love with fire. This creates passionate connections. The "dosha" is simply a reminder to channel this intensity consciously.',
        'Kaal Sarpa Dosha': 'Deep transformation energy — your chart has a karmic pattern that pushes you toward spiritual growth. This intensity, when understood, becomes a powerful catalyst.',
        'Sade Sati': 'Saturn\'s teaching period — a 7.5-year cycle of growth through discipline. Not punishment — preparation for your next level.',
        'Kantaka Shani': 'Saturn\'s focused lesson — specific areas of life are being strengthened through temporary challenge.',
    }

    frame = frames.get(name, f'{name}: a growth opportunity')
    return f"{frame} Remedy: {remedy}"


def interpret_dasha(md_lord: str, ad_lord: str, pd_lord: str) -> str:
    """Frame dasha periods as OPPORTUNITIES."""
    md_gifts = {
        'Venus': 'This is your time for building relationships, comfort, and material security. Venus brings beauty, connection, and gains through your network.',
        'Jupiter': 'Expansion and wisdom — opportunities for growth, teaching, and good fortune.',
        'Saturn': 'Mastery through discipline — what you build now lasts. Saturn rewards patience.',
        'Mars': 'Action and energy — time to compete, build, and act with courage.',
        'Mercury': 'Communication and commerce — your words and analysis create value.',
        'Sun': 'Authority and recognition — time to step into your power.',
        'Moon': 'Emotional depth and public connection — your feelings guide you to the right places.',
        'Rahu': 'Breakthrough energy — unconventional paths lead to unexpected success.',
        'Ketu': 'Spiritual depth — detachment from material opens doorways to insight.',
    }

    ad_gifts = {
        'Jupiter': 'Jupiter within Venus = expansion within comfort. Learning and growing through partnerships.',
        'Saturn': 'Saturn within Venus = building lasting structures for your gains.',
        'Venus': 'Peak of Venus energy — relationships and comfort at their strongest.',
        'Mars': 'Mars within Venus = taking action on your goals with passion.',
        'Mercury': 'Mercury within Venus = communication creates connections and value.',
    }

    md = md_gifts.get(md_lord, f'{md_lord} period')
    ad = ad_gifts.get(ad_lord, f'{ad_lord} sub-period')

    return f"Mahadasha: {md} Antardasha: {ad} Current focus: {pd_lord} Pratyantardasha."
