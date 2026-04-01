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
    """Build a comprehensive context string from all chart data."""

    asc = chart.ascendant
    planets = chart.planets

    lines = []
    lines.append(f"BIRTH DATA: {chart.name}, born {chart.birth_date} at {chart.birth_time} in {chart.birth_place}")
    lines.append(f"ASCENDANT: {asc.rashi} {asc.nakshatra} Pada {asc.pada}")
    lines.append("")

    # All planet positions
    lines.append("PLANETARY POSITIONS (D1):")
    for name in ['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn','Rahu','Ketu']:
        p = planets[name]
        retro = " (R)" if p.retrograde else ""
        lines.append(f"  {name}: {p.rashi} {p.degree_in_sign:.2f}° in H{p.house}, {p.nakshatra} Pada {p.pada}{retro}")

    lines.append("")

    # House rulerships
    lines.append("HOUSE RULERSHIPS:")
    for planet, houses in sorted(rulerships.items()):
        p = planets[planet]
        lines.append(f"  {planet}: rules H{houses}, placed in H{p.house} ({p.rashi})")

    lines.append("")

    # Yogas
    if yogas:
        lines.append("YOGAS:")
        for y in yogas:
            lines.append(f"  {y.name}: {y.description} [{y.strength}]")

    lines.append("")

    # Doshas
    if doshas:
        lines.append("DOSHAS:")
        for d in doshas:
            lines.append(f"  {d.name} ({d.severity}): {d.description}")
    else:
        lines.append("DOSHAS: None active")

    lines.append("")

    # Shadbala ranking
    if shadbala and shadbala.get('ranking'):
        lines.append("SHADBALA (planetary strength ranking):")
        for r in shadbala['ranking']:
            p = shadbala['planets'][r['planet']]
            lines.append(f"  #{r['rank']} {r['planet']}: {r['score']:.3f} ({p['dignity']}, H{p['house']})")

    lines.append("")

    # Ashtakavarga
    if ashtakavarga and ashtakavarga.get('house_scores'):
        lines.append("ASHTAKAVARGA (house strength):")
        for h in range(1, 13):
            lines.append(f"  H{h}: {ashtakavarga['house_scores'][h]} bindus")

    lines.append("")

    # D9 Navamsha
    if vargas and 'D9' in vargas:
        lines.append("D9 NAVAMSHA:")
        for p, s in vargas['D9']['signs'].items():
            lines.append(f"  {p}: {s}")

    lines.append("")

    # D10 Career
    if vargas and 'D10' in vargas:
        lines.append("D10 DASHAMAMSHA (career):")
        for p, s in vargas['D10']['signs'].items():
            lines.append(f"  {p}: {s}")

    lines.append("")

    # Conjunctions
    if conjunctions:
        lines.append("CONJUNCTIONS:")
        for c in conjunctions:
            lines.append(f"  {c['planets'][0]} + {c['planets'][1]} in H{c['house']} ({c['sign']}), orb {c['orb']}°")

    lines.append("")

    # Current dasha
    current = dasha_data.get('current', {})
    if current.get('mahadasha'):
        md = current['mahadasha']
        lines.append(f"CURRENT DASHA: {md['lord']} Mahadasha ({md['start']} to {md['end']})")
    if current.get('antardasha'):
        ad = current['antardasha']
        lines.append(f"  Antardasha: {ad['lord']} ({ad['start']} to {ad['end']})")
    if current.get('pratyantardasha'):
        pd = current['pratyantardasha']
        lines.append(f"  Pratyantardasha: {pd['lord']} ({pd['start']} to {pd['end']})")

    lines.append("")

    # Current transits (key planets)
    if transits:
        lines.append("CURRENT TRANSITS:")
        for name in ['Saturn','Jupiter','Rahu','Mars','Moon']:
            if name in transits:
                t = transits[name]
                lines.append(f"  {name}: {t['rashi']} H{t['house']} (orb from natal: {t['orb']:+.1f}°)")

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
