"""LLM Reading — AI-generated interpretive readings.

The AI receives PRE-INTERPRETED data — meanings, not raw numbers.
Its job: connect dots and add narrative.
"""

import json
import os
from .interpretations import (
    interpret_planet, interpret_conjunction, interpret_yoga,
    interpret_dosha, interpret_dasha, NAKSHATRA_INTERPS
)

# Try importing API clients
try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False


def build_chart_context(chart, rulerships, yogas, doshas, shadbala,
                        ashtakavarga, dasha_data, transits, vargas,
                        conjunctions, aspects) -> str:
    """Build PRE-INTERPRETED context — the AI receives meanings, not raw data."""

    from .interpretations import (
        interpret_full, interpret_conjunction, interpret_yoga,
        interpret_dosha, interpret_dasha, NAKSHATRA_INTERPS
    )
    from .shadbala import _get_dignity
    from .jaimini import calculate_chara_karakas, get_karakas_summary

    asc = chart.ascendant
    planets = chart.planets

    lines = []
    lines.append(f"CHART: {chart.name}, born {chart.birth_date} {chart.birth_time} in {chart.birth_place}")
    lines.append(f"ASCENDANT: {asc.rashi} {asc.nakshatra} Pada {asc.pada}")
    lines.append("")

    # === JAIMINI CHARA KARAKAS ===
    karakas = calculate_chara_karakas(planets)
    lines.append("JAIMINI CHARA KARAKAS:")
    lines.append(get_karakas_summary(karakas))
    lines.append("")

    # === PLANETS WITH PRE-COMPUTED INTERPRETATIONS ===
    lines.append("=== PLANETARY POSITIONS (with interpretations) ===")
    for name in ['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn','Rahu','Ketu']:
        p = planets[name]
        houses_ruled = rulerships.get(name, [])
        dignity = _get_dignity(name, p.rashi_index)
        d9_sign = vargas['D9']['signs'].get(name, '') if vargas else ''
        d10_sign = vargas['D10']['signs'].get(name, '') if vargas else ''

        interp = interpret_full(
            name, p.rashi, p.house, p.nakshatra, p.pada,
            p.retrograde, houses_ruled, dignity, d9_sign, d10_sign
        )
        lines.append(f"\n{name} ({p.rashi} {p.degree_in_sign:.1f}° H{p.house}):")
        lines.append(f"  {interp}")
    lines.append("")

    # === CONJUNCTIONS WITH MEANINGS ===
    if conjunctions:
        lines.append("=== CONJUNCTIONS ===")
        for c in conjunctions:
            interp = interpret_conjunction(
                c['planets'][0], c['planets'][1],
                c['house'], c['sign'], c['orb']
            )
            lines.append(f"  {interp}")
        lines.append("")

    # === YOGAS WITH MEANINGS ===
    if yogas:
        lines.append("=== YOGAS ===")
        for y in yogas:
            interp = interpret_yoga(y.name, y.planets, y.description, y.strength)
            lines.append(f"  {interp}")
        lines.append("")

    # === DOSHAS WITH MEANINGS ===
    if doshas:
        lines.append("=== DOSHAS ===")
        for d in doshas:
            interp = interpret_dosha(d.name, d.severity, d.description, d.remedy)
            lines.append(f"  {interp}")
        lines.append("")

    # === SHADBALA ===
    if shadbala and shadbala.get('ranking'):
        lines.append("=== PLANETARY STRENGTH ===")
        for r in shadbala['ranking']:
            p = shadbala['planets'][r['planet']]
            lines.append(f"  #{r['rank']} {r['planet']}: {r['score']:.3f} ({p['dignity']}, H{p['house']})")
        lines.append("")

    # === ASHTAKAVARGA ===
    if ashtakavarga and ashtakavarga.get('house_scores'):
        scores = ashtakavarga['house_scores']
        strong = [f"H{h}" for h, s in scores.items() if s >= 5]
        weak = [f"H{h}" for h, s in scores.items() if s < 4]
        lines.append("=== HOUSE STRENGTH ===")
        lines.append(f"  Strong: {', '.join(strong) if strong else 'none'}")
        lines.append(f"  Weak: {', '.join(weak) if weak else 'none'}")
        lines.append("")

    # === DASHA WITH INTERPRETATION ===
    current = dasha_data.get('current', {})
    if current.get('mahadasha'):
        md = current['mahadasha']
        ad = current.get('antardasha', {})
        pd = current.get('pratyantardasha', {})
        lines.append("=== CURRENT PERIOD ===")
        interp = interpret_dasha(md['lord'], ad.get('lord', '?'), pd.get('lord', '?'))
        lines.append(f"  {interp}")
        from datetime import date
        end = date.fromisoformat(md['end'])
        remaining = (end - date.today()).days
        lines.append(f"  {remaining} days ({remaining/365.25:.1f}y) remaining in {md['lord']} MD")
        if ad:
            end_ad = date.fromisoformat(ad['end'])
            remaining_ad = (end_ad - date.today()).days
            lines.append(f"  {remaining_ad} days remaining in {ad['lord']} AD")
        lines.append("")

    # === TRANSITS ===
    if transits:
        lines.append("=== CURRENT TRANSITS ===")
        for name in ['Saturn','Jupiter','Rahu','Mars']:
            if name in transits:
                t = transits[name]
                lines.append(f"  {name}: transiting {t['rashi']} H{t['house']}")
        lines.append("")

    return "\n".join(lines)

    return "\n".join(lines)


SYSTEM_PROMPT = """You are an expert Vedic astrologer with deep knowledge of Parashari, Jaimini, and KP systems. You analyze charts with nuance, connecting multiple factors into coherent narratives.

Your readings should:
1. SYNTHESIZE — don't just list data, connect it into meaning
2. PRIORITIZE — focus on what matters most (Yogakaraka > weak planet, current dasha > future dasha)
3. RESOLVE CONTRADICTIONS — explain when D1 and D9 differ, when a planet is strong in one system but weak in another
4. BE SPECIFIC — reference exact degrees, nakshatras, house placements
5. BE HONEST — don't sugarcoat challenges, but always mention remedies
6. TELL A STORY — the reading should flow, not be a list of disconnected facts
7. CONNECT TO TIME — always reference the current dasha and transits

Write in a direct, warm, intelligent tone. Like a wise friend who happens to know astrology deeply."""


USER_PROMPT_TEMPLATE = """Analyze this Vedic astrology chart and write a comprehensive reading.

{context}

Write a complete reading covering:
1. CORE IDENTITY — Who is this person? (Ascendant, Moon, Atmakaraka)
2. STRENGTHS — What's powerful? (Yogakaraka, strong planets, yogas, high Ashtakavarga houses)
3. CHALLENGES — What's difficult? (Debilitated planets, doshas, weak houses)
4. CAREER — Direction and timing (10th lord, D10, career yogas)
5. RELATIONSHIPS — Love and marriage (7th lord, Venus, D9, Darakaraka)
6. HEALTH — Concerns and remedies
7. CURRENT PERIOD — What's happening now? (Dasha + transits)
8. TIMING — Key dates and periods coming up
9. ADVICE — What should they do?

Be specific. Reference exact degrees, nakshatras, and house placements. Connect the dots between different parts of the chart."""


def generate_llm_reading(chart, rulerships, yogas, doshas, shadbala,
                         ashtakavarga, dasha_data, transits, vargas,
                         conjunctions, aspects,
                         provider: str = 'auto') -> str:
    """Generate an AI-powered reading using LLM API.

    Args:
        All chart data objects
        provider: 'openai', 'anthropic', or 'auto' (tries both)

    Returns:
        Reading text from the LLM
    """
    context = build_chart_context(
        chart, rulerships, yogas, doshas, shadbala,
        ashtakavarga, dasha_data, transits, vargas,
        conjunctions, aspects
    )

    user_prompt = USER_PROMPT_TEMPLATE.format(context=context)

    # Try providers
    if provider == 'auto':
        if HAS_ANTHROPIC and os.environ.get('ANTHROPIC_API_KEY'):
            provider = 'anthropic'
        elif HAS_OPENAI and os.environ.get('OPENAI_API_KEY'):
            provider = 'openai'
        else:
            return _fallback_reading(chart, yogas, doshas, dasha_data)

    if provider == 'anthropic':
        return _call_anthropic(user_prompt)
    elif provider == 'openai':
        return _call_openai(user_prompt)
    else:
        return _fallback_reading(chart, yogas, doshas, dasha_data)


def _call_anthropic(prompt: str) -> str:
    """Call Anthropic Claude API."""
    try:
        client = anthropic.Anthropic()
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text
    except Exception as e:
        return f"Error calling Anthropic API: {e}"


def _call_openai(prompt: str) -> str:
    """Call OpenAI API."""
    try:
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model="gpt-4o",
            max_tokens=4000,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error calling OpenAI API: {e}"


def _fallback_reading(chart, yogas, doshas, dasha_data) -> str:
    """Fallback reading without LLM — basic synthesis."""
    lines = []
    asc = chart.ascendant
    lines.append(f"Your Ascendant is {asc.rashi} ({asc.nakshatra} Pada {asc.pada}).")

    if yogas:
        lines.append(f"\nYogas found: {', '.join(y.name for y in yogas)}")

    if doshas:
        lines.append(f"\nDoshas: {', '.join(d.name for d in doshas)}")
    else:
        lines.append("\nNo active doshas detected.")

    current = dasha_data.get('current', {})
    if current.get('mahadasha'):
        lines.append(f"\nCurrent period: {current['mahadasha']['lord']} Mahadasha, {current.get('antardasha', {}).get('lord', '?')} Antardasha.")

    lines.append("\nFor a detailed AI reading, configure an LLM API key (ANTHROPIC_API_KEY or OPENAI_API_KEY).")

    return "\n".join(lines)
