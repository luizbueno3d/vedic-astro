"""LLM reading orchestration for layered astrology readings.

The chart data is already computed by the engine. This module prepares a richer
context, adds Bhava Chalit Chart (BCC) / KP house shifts, and runs a staged AI
analysis so the final reading is deeper than a single prompt dump.
"""

from .ai_provider import generate_reading as ai_generate_reading, get_active_provider
from .bhavat_bhavam import get_planet_house_from_house_analysis
from .interpretations import interpret_conjunction, interpret_dasha, interpret_dosha, interpret_full, interpret_yoga
from datetime import date

from .jaimini import calculate_chara_karakas, calculate_chara_dasha, calculate_jaimini_raja_yoga, calculate_karakamsa, get_jaimini_interpretation, get_jaimini_sign_aspects, get_karakas_priority_notes, get_karakas_summary, interpret_chara_dasha, interpret_karakamsa
from .kp import calculate_kp_bhava_chalit


HOUSE_TOPICS = {
    1: 'identity, body, presence',
    2: 'wealth, family, speech',
    3: 'skills, effort, communication',
    4: 'home, roots, inner security',
    5: 'creativity, children, intelligence',
    6: 'service, health, conflict, discipline',
    7: 'partnership, clients, public dealings',
    8: 'transformation, secrecy, crisis, occult',
    9: 'dharma, teachers, luck, higher wisdom',
    10: 'career, authority, visible karma',
    11: 'gains, networks, ambitions',
    12: 'loss, solitude, foreign lands, moksha',
}


READING_PRIORITIES = """READING PRIORITY HIERARCHY

PRIMARY LAYERS - these build the core reading and outrank everything below:
1. D1 baseline: lagna, lagna lord, Moon, Sun, house lords, dignity, conjunctions, aspects.
2. Planet condition check: before concluding on a planet, inspect dignity, friend/enemy sign, combustion, and rulership.
3. House judgment: judge houses through their lords before jumping to yogas or abstractions.
4. Timing backbone: current dasha first, then sub-periods, then transits.

SECONDARY LAYERS - these refine the main reading but must not override the primary layers:
5. Nakshatra and pada refine expression after sign-house-lordship is understood.
6. BCC/KP shows where results manifest, especially in dasha. It does not erase natal D1 nature.
7. Jaimini karakas add a second-pass lens for soul purpose, vocation, and partnership patterns.
8. Bhavat Bhavam shows the derived house through which a placement matures or manifests secondarily.
9. Shadbala and Ashtakavarga are weighting tools. Use them to judge intensity and ease, not to replace chart structure.

TOPIC-SPECIFIC LAYERS - only use when the topic requires them:
10. D9 for relationship, inner maturity, and deeper planetary support.
11. D10 for career, public role, and professional manifestation.
12. D7 and D12 only when discussing children/lineage or parents/ancestry.

CONSTRAINTS:
- Never let a secondary or topic-specific layer overrule a clear primary-layer statement unless the context explicitly says it modifies manifestation rather than replacing it.
- If two layers disagree, explain the hierarchy and the blend instead of flattening them into one vague statement.
"""


LAYER_USAGE_PROTOCOL = """LAYER USAGE PROTOCOL

When writing the reading, explicitly signal why a layer is being used.

- Primary layer wording: "First we look at... because this is the base structure." 
- Secondary layer wording: "Next we refine that picture with..."
- Topic-specific layer wording: "For career specifically..." or "In relationship matters..."

Do not introduce D9, D10, Jaimini, Bhavat Bhavam, BCC, Shadbala, or Ashtakavarga as if they are equal to the D1 foundation.
Always tell the reader whether a layer is:
- foundational
- refining
- timing
- topic-specific

If using BCC, say it modifies manifestation.
If using Jaimini, say it adds a role-based lens.
If using Bhavat Bhavam, say it adds a derivative-house reinforcement layer.
If using D9 or D10, say they confirm and specialize rather than replace D1.
"""


GUIDED_FLOW = """GUIDED FLOW FOR THE READER

The reading should mirror the app's learning path.

Recommended order for the human reader:
1. D1 foundation - who the person is and what the chart is built on.
2. Timing - what is active now through dasha and transit.
3. Deeper logic - yogas, Jaimini, Bhavat Bhavam, and structural modifiers.
4. Topic charts - D9, D10, D7, D12 only when the topic specifically calls for them.
5. Synthesis - practical conclusions and advice.

When useful, say this explicitly in the reading so the reader feels guided rather than flooded.
"""


READING_BLUEPRINT = """FINAL READING BLUEPRINT

Write the reading in this exact order, with explicit section headers.

1. Cosmic Blueprint
- 2-4 paragraphs only.
- Start by telling the reader why this section comes first.
- Add a brief sentence that this reading will move from foundation, to timing, to deeper modifiers, to topic-specific charts.
- State the core paradox of the chart.
- Name the D1 ascendant, Moon, Atmakaraka, and the main BCC shift pattern.
- Say what kind of human being this chart describes before discussing life areas.

2. Key BCC Shifts
- Bullet list.
- One-line intro explaining that D1 shows natal setup, while BCC shows where results land in real life.
- Use literal notation such as: Mercury: D1 H8 -> BCC H7.
- Only include the most meaningful shifts.
- After each shift, add one short clause about how manifestation changes.
- Do not force BCC into planets that do not materially shift or into sections where D1 already explains the point well.

3. Identity and Psychology
- Explain the inner self using D1.
- Explain how the world experiences the person using BCC when relevant.
- Resolve contradictions instead of listing them.

4. Strengths and Natural Gifts
- Focus on the strongest planets, yogas, house strengths, and supportive varga confirmations.
- Explain why these strengths matter in real life.

5. Friction, Blind Spots, and Lessons
- Cover difficult planets, weak houses, doshas, and internal tensions.
- Be honest but not dramatic.
- Every challenge must include the mechanism of the problem, not just the label.

6. Career, Work, and Material Direction
- Use 10th house logic, relevant yogas, D10, and BCC operational shifts.
- Explain how work actually manifests, not just ideal professions.

7. Relationships and Intimacy
- Use 7th house logic, Venus, Moon, D9, and BCC when it changes the lived expression.
- Distinguish between what the native wants, what they attract, and how relationship karma manifests.

8. Health, Energy, and Nervous System
- Keep it grounded.
- Talk about stress patterns, depletion patterns, recovery style, and practical regulation.

9. Spiritual Pattern and Inner Evolution
- Use 8th, 9th, 12th houses, Ketu, Jupiter, Moon, and any strong moksha signatures.
- Explain the actual doorway to growth.

10. Current Dasha and Active Timing
- This is one of the most important sections.
- Introduce this section as the second major thing to check after the natal foundation.
- Briefly explain in plain language that dasha means time period, antardasha means sub-period, and pratyantardasha means the smaller active trigger inside it.
- For Mahadasha, Antardasha, and Pratyantardasha lords, explain:
  - what the planet means naturally
  - what it does in D1
  - where it manifests in BCC
  - what this means in lived reality now
- If D1 and BCC differ, explicitly explain the blend.

11. Practical Advice Now
- End with concrete advice.
- Give specific behavioral guidance, not generic spirituality.
- Make it feel earned by the chart.

EXPLANATION RULES FOR NON-ASTROLOGERS
- Assume the reader is intelligent but new to astrology.
- Whenever you introduce a Sanskrit or technical term, explain it in plain English immediately.
- Tell the reader why each section matters before interpreting it.
- Make the order visible: say first, second, third, next, finally when useful.
- Do not drown the reader in jargon. Translate, then interpret.
- If something is especially important, say that clearly and explain why it outranks the next layer.
- In the opening sections, explicitly orient the reader with phrases like "First we look at..." and "Next we look at...".

STYLE RULES
- Follow the reading priority hierarchy supplied in the context.
- Follow the layer usage protocol supplied in the context.
- Follow the guided flow supplied in the context.
- No example stories unless directly tied to chart logic.
- No generic astrology filler.
- No unsupported claims.
- Never invent placements or karakas.
- Rahu and Ketu are NOT Jaimini chara karakas.
- Do not rename BCC as D7, Saptamsha, or any other varga.
- Use only the data explicitly present in the supplied context.
- If something is uncertain, speak cautiously instead of hallucinating.
"""


FACT_GUARDRAILS = """FACT GUARDRAILS

- Chara karakas in this system use 7 classical planets only.
- Rahu and Ketu never become Atmakaraka, Amatyakaraka, Darakaraka, or any other chara karaka here.
- D1 = natal architecture.
- Moon is the secondary lived lens after lagna, especially for mental and emotional experience.
- Planet condition must include dignity, relationship to sign lord (friend/enemy/neutral), and combustion when available.
- BCC = operative manifestation field, especially important for dasha results.
- BCC is not D7.
- Use BCC selectively: strongest in dasha/event manifestation, secondary in character reading unless the house shift is highly meaningful.
- Do not override the supplied chart facts with your own remembered astrology rules.
- If the context says a planet is D1 H8 and BCC H7, preserve that exactly.
"""


def _format_house_list(houses: list[int]) -> str:
    if not houses:
        return 'none'
    return ', '.join(f'H{house}' for house in houses)


def _build_bcc_shift_note(d1_house: int, bcc_house: int) -> str:
    if d1_house == bcc_house:
        return f'D1 and BCC both agree on H{d1_house}.'

    d1_topic = HOUSE_TOPICS.get(d1_house, f'H{d1_house}')
    bcc_topic = HOUSE_TOPICS.get(bcc_house, f'H{bcc_house}')
    return (
        f'D1 starts from H{d1_house} ({d1_topic}), but the BCC operative field '
        f'manifests through H{bcc_house} ({bcc_topic}). Read this as blended: '
        f'the planet keeps its natal nature, but events land through the BCC house.'
    )


def _get_bcc_house(kp_data, planet_name: str, fallback_house: int) -> int:
    bcc_house = kp_data.planet_houses.get(planet_name)
    if bcc_house is None:
        return fallback_house
    return bcc_house


def _append_dasha_lord_context(lines: list[str], chart, rulerships: dict[str, list[int]],
                               dasha_data: dict, kp_data) -> None:
    current = dasha_data.get('current', {})
    if not current:
        return

    lines.append('=== CURRENT PERIOD (DASHA + BCC OPERATIVE HOUSES) ===')
    interp = interpret_dasha(
        current.get('mahadasha', {}).get('lord', '?'),
        current.get('antardasha', {}).get('lord', '?'),
        current.get('pratyantardasha', {}).get('lord', '?'),
    )
    lines.append(f'Current dasha interpretation: {interp}')

    for period_key, label in [
        ('mahadasha', 'Mahadasha'),
        ('antardasha', 'Antardasha'),
        ('pratyantardasha', 'Pratyantardasha'),
    ]:
        period = current.get(period_key)
        if not period:
            continue

        lord = period['lord']
        planet = chart.planets.get(lord)
        if not planet:
            continue

        bcc_house = _get_bcc_house(kp_data, lord, planet.house)
        ruled_houses = rulerships.get(lord, [])
        lines.append(
            f'{label}: {lord} ({period["start"]} to {period["end"]}) | '
            f'D1 H{planet.house} | BCC H{bcc_house} | Rules {_format_house_list(ruled_houses)} | '
            f'{planet.rashi} {planet.nakshatra} Pada {planet.pada}'
        )
        lines.append(f'  {_build_bcc_shift_note(planet.house, bcc_house)}')

    lines.append('')


def build_chart_context(chart, rulerships, yogas, doshas, shadbala,
                        ashtakavarga, dasha_data, transits, vargas,
                        conjunctions, aspects, kp_data=None) -> str:
    """Build a rich reading context with D1 + BCC/KP layers."""
    from .shadbala import _get_dignity, get_combustion_status, get_sign_relationship

    if kp_data is None:
        kp_data = calculate_kp_bhava_chalit(chart)

    asc = chart.ascendant
    planets = chart.planets

    lines = []
    lines.append(f'CHART: {chart.name}, born {chart.birth_date} {chart.birth_time} in {chart.birth_place}')
    lines.append(READING_PRIORITIES)
    lines.append(LAYER_USAGE_PROTOCOL)
    lines.append(GUIDED_FLOW)
    lines.append(f'D1 ASCENDANT: {asc.rashi} {asc.nakshatra} Pada {asc.pada}')
    lines.append(
        f'BCC ASCENDANT: {kp_data.kp_asc_rashi} (KP effective ascendant, idx={kp_data.kp_asc_idx}) | '
        f'D1 asc idx={kp_data.d1_asc_idx}'
    )
    lines.append('BCC = Bhava Chalit Chart using KP / Nakshatra Nadi logic. For dashas, treat BCC as the operative event field.')
    lines.append('')

    karakas = calculate_chara_karakas(planets)
    jaimini_interpretation = get_jaimini_interpretation(karakas)
    jaimini_raja_yogas = calculate_jaimini_raja_yoga(karakas)
    karakamsa = calculate_karakamsa(karakas, planets)
    jaimini_sign_aspects = get_jaimini_sign_aspects(planets)
    chara_dasha = calculate_chara_dasha(planets, asc.rashi_index, date.fromisoformat(chart.birth_date))
    lines.append('=== JAIMINI CHARA KARAKAS ===')
    lines.append(get_karakas_summary(karakas))
    lines.append(get_karakas_priority_notes(karakas))
    lines.append('')

    lines.append('=== JAIMINI INTERPRETIVE LAYER ===')
    if jaimini_interpretation.get('atmakaraka'):
        lines.append(jaimini_interpretation['atmakaraka'])
    if jaimini_interpretation.get('darakaraka'):
        lines.append(jaimini_interpretation['darakaraka'])
    if jaimini_raja_yogas:
        for yoga in jaimini_raja_yogas:
            lines.append(f"Jaimini Raja Yoga: {yoga['description']}")
    else:
        lines.append('No active Jaimini Raja Yoga detected from the current karaka relationships.')
    if karakamsa:
        lines.append(f"Karakamsa/Swamsa: {interpret_karakamsa(karakamsa)}")
    if jaimini_sign_aspects:
        lines.append('Jaimini sign aspects:')
        for aspect in jaimini_sign_aspects[:16]:
            lines.append(f"  {aspect['from']} in {aspect['from_sign']} -> {aspect['to']} in {aspect['to_sign']}")
    if chara_dasha:
        lines.append(f"Chara Dasha: {interpret_chara_dasha(chara_dasha, karakamsa)}")
        if chara_dasha.get('current'):
            current_cd = chara_dasha['current']
            lines.append(
                f"Current Chara Dasha sign: {current_cd['sign']} ({current_cd['start']} to {current_cd['end']}) | "
                f"Lord {current_cd['lord']} in {current_cd['lord_sign']} | {current_cd['direction']}"
            )
    lines.append('')

    lines.append('=== FOUNDATIONAL READING ORDER ===')
    lines.append('Read lagna, lagna lord, Moon, Sun, house lords, conjunctions, and aspects before yogas or timing.')
    lines.append('Use nakshatra/pada for refinement, vargas for confirmation, dasha for timing, and BCC for manifestation.')
    lines.append('')

    lines.append('=== PLANETARY POSITIONS (D1 + BCC) ===')
    sun_longitude = planets['Sun'].longitude
    for name in ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu']:
        planet = planets[name]
        bcc_house = _get_bcc_house(kp_data, name, planet.house)
        houses_ruled = rulerships.get(name, [])
        dignity = _get_dignity(name, planet.rashi_index)
        relationship = get_sign_relationship(name, planet.rashi_index)
        combustion = get_combustion_status(name, planet.longitude, sun_longitude, planet.retrograde)
        d9_sign = vargas['D9']['signs'].get(name, '') if vargas else ''
        d10_sign = vargas['D10']['signs'].get(name, '') if vargas else ''
        interp = interpret_full(
            name, planet.rashi, planet.house, planet.nakshatra, planet.pada,
            planet.retrograde, houses_ruled, dignity, d9_sign, d10_sign
        )

        lines.append(
            f'{name}: {planet.rashi} {planet.degree_in_sign:.1f} deg | '
            f'D1 H{planet.house} | BCC H{bcc_house} | '
            f'Nakshatra {planet.nakshatra} Pada {planet.pada} | Rules {_format_house_list(houses_ruled)} | '
            f'Sign status {dignity} | Relationship to sign lord {relationship} | {combustion}'
        )
        lines.append(f'  {_build_bcc_shift_note(planet.house, bcc_house)}')
        lines.append(f'  {interp}')
    lines.append('')

    lines.append('=== BCC SHIFT SUMMARY ===')
    for name in ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu']:
        planet = planets[name]
        bcc_house = _get_bcc_house(kp_data, name, planet.house)
        if planet.house != bcc_house:
            lines.append(f'{name}: D1 H{planet.house} -> BCC H{bcc_house}')
    lines.append('Use the shift summary especially for dasha interpretation: D1 = natal base, BCC = real delivery channel.')
    lines.append('')

    if conjunctions:
        lines.append('=== CONJUNCTIONS ===')
        for conjunction in conjunctions:
            lines.append(
                interpret_conjunction(
                    conjunction['planets'][0],
                    conjunction['planets'][1],
                    conjunction['house'],
                    conjunction['sign'],
                    conjunction['orb'],
                )
            )
        lines.append('')

    if aspects:
        lines.append('=== ASPECTS ===')
        sorted_aspects = sorted(aspects, key=lambda aspect: aspect.get('orb', 999))
        for aspect in sorted_aspects[:18]:
            lines.append(
                f"{aspect['from']} -> {aspect['to']} | {aspect['type']} | "
                f"H{aspect['from_house']} -> H{aspect['to_house']} | orb {aspect['orb']}"
            )
        lines.append('')

    if yogas:
        lines.append('=== YOGAS ===')
        for yoga in yogas:
            lines.append(interpret_yoga(yoga.name, yoga.planets, yoga.description, yoga.strength))
        lines.append('')

    if doshas:
        lines.append('=== DOSHAS ===')
        for dosha in doshas:
            lines.append(interpret_dosha(dosha.name, dosha.severity, dosha.description, dosha.remedy))
        lines.append('')

    if shadbala and shadbala.get('ranking'):
        lines.append('=== PLANETARY STRENGTH ===')
        for rank in shadbala['ranking']:
            planet_data = shadbala['planets'][rank['planet']]
            lines.append(
                f"#{rank['rank']} {rank['planet']}: {rank['score']:.3f} "
                f"({planet_data['dignity']}, H{planet_data['house']})"
            )
        lines.append('')

    if ashtakavarga and ashtakavarga.get('house_scores'):
        scores = ashtakavarga['house_scores']
        strong = [f'H{house}' for house, score in scores.items() if score >= 5]
        weak = [f'H{house}' for house, score in scores.items() if score < 4]
        lines.append('=== HOUSE STRENGTH ===')
        lines.append(f"Strong: {', '.join(strong) if strong else 'none'}")
        lines.append(f"Weak: {', '.join(weak) if weak else 'none'}")
        lines.append('')

    planet_bb = get_planet_house_from_house_analysis(planets)
    lines.append('=== BHAVAT BHAVAM BY PLANET ===')
    lines.append('Use derivative-house logic: if a planet is in Hn, count n houses from Hn to get the secondary manifestation field.')
    for item in planet_bb:
        lines.append(f"{item['planet']}: D1 H{item['house']} -> derived H{item['bb_house']}")
        lines.append(f"  {item['count_explanation']}")
        lines.append(f"  {item['practical']}")
    lines.append('')

    _append_dasha_lord_context(lines, chart, rulerships, dasha_data, kp_data)

    if transits:
        lines.append('=== CURRENT TRANSITS ===')
        for name in ['Saturn', 'Jupiter', 'Rahu', 'Mars']:
            if name in transits:
                transit = transits[name]
                lines.append(f"{name}: transiting {transit['rashi']} H{transit['house']}")
        lines.append('')

    if vargas:
        lines.append('=== DIVISIONAL SNAPSHOT ===')
        if 'D9' in vargas:
            lines.append(f"D9 Asc: {vargas['D9']['signs'].get('Asc', '?')}")
            if vargas['D9'].get('reading', {}).get('summary'):
                lines.append(f"D9 Summary: {vargas['D9']['reading']['summary']}")
        if 'D10' in vargas:
            lines.append(f"D10 Asc: {vargas['D10']['signs'].get('Asc', '?')}")
            if vargas['D10'].get('reading', {}).get('summary'):
                lines.append(f"D10 Summary: {vargas['D10']['reading']['summary']}")
        for varga_id in ['D7', 'D12']:
            if varga_id in vargas and vargas[varga_id].get('reading', {}).get('summary'):
                lines.append(f"{varga_id} Summary: {vargas[varga_id]['reading']['summary']}")
        lines.append('')

    return '\n'.join(lines)


def _run_stage(system_prompt: str, user_prompt: str, owner_email: str | None = None) -> str:
    full_system_prompt = f"{FACT_GUARDRAILS}\n\n{system_prompt}"
    result = ai_generate_reading(full_system_prompt, user_prompt, owner_email=owner_email)
    return result.strip()


def generate_llm_reading(chart, rulerships, yogas, doshas, shadbala,
                         ashtakavarga, dasha_data, transits, vargas,
                         conjunctions, aspects,
                         provider: str = 'active', owner_email: str | None = None) -> str:
    """Generate a staged AI reading with BCC-aware dasha interpretation."""
    kp_data = calculate_kp_bhava_chalit(chart)
    context = build_chart_context(
        chart, rulerships, yogas, doshas, shadbala,
        ashtakavarga, dasha_data, transits, vargas,
        conjunctions, aspects, kp_data=kp_data,
    )

    active_provider = get_active_provider(owner_email)
    if provider == 'active' and not active_provider:
        return _fallback_reading(chart, yogas, doshas, dasha_data, kp_data)

    if active_provider and _should_use_single_pass(active_provider):
        return _generate_single_pass_reading(context, owner_email)

    stage_one = _run_stage(
        """You are a senior Vedic astrologer. Produce analyst notes, not the final reading.

Focus on:
- core identity from D1 Ascendant, lagna lord, Moon, Sun, Atmakaraka, strongest planets, yogas
- contradictions and tensions in the chart
- what is psychologically central versus socially visible

Rules:
- foundation first: lagna, lagna lord, Moon, Sun, house lords, conjunctions, aspects before yogas
- do not ignore friend sign, enemy sign, or combustion status when judging a planet
- clearly label what is primary structure versus later refinement
- be concrete and chart-specific
- mention exact signs, nakshatras, houses when relevant
- write 5-8 dense bullet points
- do not write generic astrology filler
- do not invent or re-rank karakas beyond the supplied Jaimini summary""",
        f"""Study this chart context and extract the deepest identity-level notes.

{context}""",
        owner_email,
    )

    stage_two = _run_stage(
        """You are a KP / Nakshatra Nadi specialist. Produce analyst notes, not the final reading.

Your job is to explain Bhava Chalit Chart (BCC) shifts.
- D1 gives natal nature and surface storyline
- BCC gives the operative field where results manifest
- during dasha, prioritize BCC houses for event delivery
- when D1 and BCC differ, explain the blended manifestation clearly

Rules:
- focus hard on planets that shift houses
- preserve natal sign nature; explain only the house manifestation shift
- explicitly call BCC a secondary manifestation layer, not the base chart
- do not mention BCC where there is no meaningful shift or where it adds no interpretive value
- give practical examples of blended manifestation
- especially analyze the current Mahadasha, Antardasha, and Pratyantardasha lords
- write 6-10 bullet points
- do not discuss Jaimini karakas unless they appear in the supplied context""",
        f"""Analyze this chart with special emphasis on BCC/KP shifts and dasha activation.

{context}""",
        owner_email,
    )

    stage_three = _run_stage(
        """You are a predictive astrologer. Produce analyst notes, not the final reading.

Focus on:
- current dasha and transit timing
- career, relationships, health, and spiritual evolution
- concrete near-term themes and what the person should actually do

Rules:
- dasha first, transit second
- prioritize what is active now over abstract potential
- if a dasha lord is combust or placed in an enemy sign, factor that into the tone of results
- when using D9, D10, D7, or D12, state that these are topic-specific support layers
- use D9 and D10 where helpful
- include tensions, not just strengths
- write 6-10 bullet points
- ground every prediction in supplied chart facts""",
        f"""Extract predictive and practical timing notes from this chart context.

{context}""",
        owner_email,
    )

    return _run_stage(
        f"""You are an expert Vedic astrologer writing a long-form premium reading.

This reading must feel deep, specific, and layered - not shallow.

Core framework:
- D1 = natal architecture and psychological baseline
- BCC (Bhava Chalit Chart, KP / Nakshatra Nadi) = operative field where results manifest
- During dasha interpretation, always integrate both, but give BCC special weight for event manifestation
- Outside timing, use BCC only when a shift materially changes interpretation.

Priority discipline:
- primary layers outrank secondary layers
- secondary layers refine but do not replace primary layers
- topic-specific layers should appear only when the life area calls for them
- if there is tension between layers, explain the hierarchy before explaining the blend

Reader guidance discipline:
- do not throw the reader into advanced material without orienting them first
- make the reading feel like a guided walk through the chart
- briefly tell the reader what comes first, what comes second, and what comes later
- the final reading should feel aligned with the app flow: foundation -> timing -> deeper logic -> topic-specific charts -> synthesis

{READING_BLUEPRINT}

Writing requirements:
- 1600 to 2600 words
- follow the blueprint exactly
- make the reading pedagogical: explain what the reader should look at first and why
- in the opening, include a short roadmap sentence that tells the reader the reading will move from foundation, to timing, to deeper modifiers, to topic-specific charts, and finally advice
- explicitly tell the reader whether a section is foundational, refining, timing-based, or topic-specific
- explicitly explain important D1 vs BCC house shifts
- if a dasha lord shifts houses in BCC, name both houses and explain how the result blends
- be warm, intelligent, direct, and nuanced
- no fluff, no repetition, no vague motivational filler
- do not mention that this was produced in stages""",
        f"""Write the final reading using the chart context and the analyst notes below.

CHART CONTEXT
{context}

IDENTITY NOTES
{stage_one}

BCC / KP NOTES
{stage_two}

        TIMING NOTES
{stage_three}""",
        owner_email,
    )


def _should_use_single_pass(provider) -> bool:
    if provider.name == 'openrouter' and ':free' in provider.model:
        return True
    if provider.name == 'groq':
        return True
    return False


def _generate_single_pass_reading(context: str, owner_email: str | None = None) -> str:
    """Use one call for rate-limited/free providers."""
    return _run_stage(
        f"""You are an expert Vedic astrologer writing a long-form premium reading.

Use one single pass only. The provider is likely rate-limited, so you must produce the final answer without relying on intermediate steps.

Core framework:
- D1 = natal architecture and psychological baseline
- BCC (Bhava Chalit Chart, KP / Nakshatra Nadi) = operative field where results manifest
- During dasha interpretation, integrate both, but give BCC special weight for event manifestation

Priority discipline:
- primary layers outrank secondary layers
- secondary layers refine but do not replace primary layers
- topic-specific layers should appear only when the life area calls for them

Reader guidance discipline:
- make the reading feel like a guided walk through the chart
- briefly tell the reader what comes first, what comes second, and what comes later

{READING_BLUEPRINT}

Writing requirements:
- 1600 to 2600 words
- follow the blueprint exactly
- include a short roadmap sentence near the beginning
- explain terms in plain English for non-astrologers
- be warm, nuanced, specific, and non-generic""",
        f"""Write the final reading from this chart context.

{context}""",
        owner_email,
    )


def _fallback_reading(chart, yogas, doshas, dasha_data, kp_data) -> str:
    """Fallback reading without an active AI provider."""
    lines = []
    asc = chart.ascendant
    lines.append(f'Your Ascendant is {asc.rashi} ({asc.nakshatra} Pada {asc.pada}).')
    lines.append(f'Your BCC ascendant is {kp_data.kp_asc_rashi}.')

    current = dasha_data.get('current', {})
    if current.get('mahadasha'):
        md_lord = current['mahadasha']['lord']
        planet = chart.planets.get(md_lord)
        if planet:
            lines.append(
                f'Current Mahadasha: {md_lord}. Natal house H{planet.house}; '
                f'BCC operative house H{_get_bcc_house(kp_data, md_lord, planet.house)}.'
            )
    if current.get('antardasha'):
        ad_lord = current['antardasha']['lord']
        planet = chart.planets.get(ad_lord)
        if planet:
            lines.append(
                f'Current Antardasha: {ad_lord}. Natal house H{planet.house}; '
                f'BCC operative house H{_get_bcc_house(kp_data, ad_lord, planet.house)}.'
            )

    if yogas:
        lines.append(f"Yogas found: {', '.join(yoga.name for yoga in yogas)}")
    if doshas:
        lines.append(f"Doshas found: {', '.join(dosha.name for dosha in doshas)}")

    lines.append('Configure an AI provider on the AI Interpretations page to generate the new layered BCC-aware reading.')
    return '\n\n'.join(lines)
