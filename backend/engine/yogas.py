"""Yoga detection — automatic identification of planetary combinations."""

from dataclasses import dataclass
from .ephemeris import PlanetPosition, RASHI_LORDS, get_rashi_lord

# Kendra houses (1, 4, 7, 10) and Trikona houses (1, 5, 9)
KENDRA = {1, 4, 7, 10}
TRIKONA = {1, 5, 9}
UPACHAYA = {3, 6, 10, 11}  # Houses that grow with time
DUSTHANA = {6, 8, 12}       # Houses of difficulty


def calculate_house_rulerships(asc_rashi_index: int) -> dict[str, list[int]]:
    """Calculate which houses each planet rules based on Ascendant.

    Args:
        asc_rashi_index: 0-11, the rashi index of the Ascendant

    Returns:
        dict of {planet_name: [list of houses it rules]}
    """
    planet_houses = {}
    for house in range(1, 13):
        rashi_idx = (asc_rashi_index + house - 1) % 12
        lord = RASHI_LORDS[rashi_idx]
        planet_houses.setdefault(lord, []).append(house)
    return planet_houses


@dataclass
class Yoga:
    name: str
    planets: list[str]
    description: str
    strength: str  # 'strong', 'moderate', 'weak'
    houses_involved: list[int]


# ===== MAJOR YOGAS =====

def detect_raja_yoga(planets: dict[str, PlanetPosition],
                     planet_houses_ruled: dict[str, list[int]] = None) -> list[Yoga]:
    """Raja Yoga: Kendra lord + Trikona lord conjunction or mutual aspect.

    The most powerful yoga for success and authority.
    Requires planet_houses_ruled dict (planet → [houses it rules]).
    """
    yogas = []

    if not planet_houses_ruled:
        return yogas  # Can't detect without rulership info

    # Find which planets rule Kendra and Trikona houses
    # H1 is excluded from both (it's an overlap, not a true Kendra+Trikona)
    PURE_KENDRA = {4, 7, 10}
    PURE_TRIKONA = {5, 9}
    kendra_lords = set()
    trikona_lords = set()
    for planet, houses in planet_houses_ruled.items():
        for h in houses:
            if h in PURE_KENDRA:
                kendra_lords.add(planet)
            if h in PURE_TRIKONA:
                trikona_lords.add(planet)

    # Check for conjunctions between Kendra and Trikona lords
    for k_lord in kendra_lords:
        for t_lord in trikona_lords:
            if k_lord == t_lord:
                continue  # Same planet, skip (but note Yogakaraka separately)
            if k_lord in planets and t_lord in planets:
                k = planets[k_lord]
                t = planets[t_lord]
                # Same sign = conjunction
                if k.rashi_index == t.rashi_index:
                    # Check if same planet is both Kendra and Trikona lord (Yogakaraka)
                    is_yogakaraka = k_lord in trikona_lords or t_lord in kendra_lords
                    label = 'Yogakaraka Raja Yoga' if is_yogakaraka else 'Raja Yoga'
                    yogas.append(Yoga(
                        name=label,
                        planets=[k_lord, t_lord],
                        description=f'{k_lord} (rules H{planet_houses_ruled[k_lord]}) conjunct {t_lord} (rules H{planet_houses_ruled[t_lord]}) in H{k.house}',
                        strength='strong',
                        houses_involved=[k.house]
                    ))

    return yogas


def detect_dhana_yoga(planets: dict[str, PlanetPosition],
                     planet_houses_ruled: dict[str, list[int]] = None) -> list[Yoga]:
    """Dhana Yoga: Connection between 2nd/11th house lords (wealth)."""
    yogas = []
    if not planet_houses_ruled:
        return yogas

    # Find planets that rule 2nd and 11th houses
    lord_2 = None
    lord_11 = None
    for planet, houses in planet_houses_ruled.items():
        if 2 in houses:
            lord_2 = planet
        if 11 in houses:
            lord_11 = planet

    if lord_2 and lord_11 and lord_2 != lord_11 and lord_2 in planets and lord_11 in planets:
        p2 = planets[lord_2]
        p11 = planets[lord_11]
        if p2.rashi_index == p11.rashi_index:
            yogas.append(Yoga(
                name='Dhana Yoga',
                planets=[lord_2, lord_11],
                description=f'{lord_2} (2nd lord) conjunct {lord_11} (11th lord) — strong wealth indicator',
                strength='strong',
                houses_involved=[2, 11]
            ))

    return yogas


def detect_viparita_raja_yoga(planets: dict[str, PlanetPosition],
                              planet_houses_ruled: dict[str, list[int]] = None) -> list[Yoga]:
    """Viparita Raja Yoga: Dusthana lords (6/8/12) in other dusthana houses."""
    yogas = []
    if not planet_houses_ruled:
        return yogas

    # Find which planets rule dusthana houses
    dusthana_lords = {}
    for planet, houses in planet_houses_ruled.items():
        for h in houses:
            if h in DUSTHANA:
                dusthana_lords[h] = planet

    for house, lord in dusthana_lords.items():
        if lord in planets:
            p = planets[lord]
            if p.house in DUSTHANA and p.house != house:
                yoga_names = {
                    (6, 8): 'Harsha Viparita Raja Yoga',
                    (6, 12): 'Harsha Viparita Raja Yoga',
                    (8, 6): 'Sarala Viparita Raja Yoga',
                    (8, 12): 'Sarala Viparita Raja Yoga',
                    (12, 6): 'Vimala Viparita Raja Yoga',
                    (12, 8): 'Vimala Viparita Raja Yoga',
                }
                name = yoga_names.get((house, p.house), 'Viparita Raja Yoga')
                yogas.append(Yoga(
                    name=name,
                    planets=[lord],
                    description=f'{lord} ({house}th lord) in H{p.house} — success through adversity',
                    strength='moderate',
                    houses_involved=[house, p.house]
                ))

    return yogas


def detect_gaja_kesari_yoga(planets: dict[str, PlanetPosition]) -> list[Yoga]:
    """Gaja Kesari Yoga: Moon and Jupiter in Kendra from each other.

    Wisdom, fame, and prosperity.
    """
    yogas = []
    if 'Moon' not in planets or 'Jupiter' not in planets:
        return yogas

    moon = planets['Moon']
    jupiter = planets['Jupiter']

    # House distance from Moon to Jupiter
    dist = (jupiter.rashi_index - moon.rashi_index) % 12

    # Kendra from each other = 0, 3, 6, 9 (same, 4th, 7th, 10th)
    if dist in (0, 3, 6, 9):
        houses = {0: 'same house', 3: '4th', 6: '7th', 9: '10th'}
        yogas.append(Yoga(
            name='Gaja Kesari Yoga',
            planets=['Moon', 'Jupiter'],
            description=f'Moon and Jupiter in Kendra ({houses[dist]}) — wisdom and prosperity',
            strength='strong' if dist == 0 else 'moderate',
            houses_involved=[moon.house, jupiter.house]
        ))

    return yogas


def detect_budhaditya_yoga(planets: dict[str, PlanetPosition]) -> list[Yoga]:
    """Budhaditya Yoga: Sun and Mercury conjunction.

    Intelligence, communication skills, business acumen.
    """
    yogas = []
    if 'Sun' not in planets or 'Mercury' not in planets:
        return yogas

    sun = planets['Sun']
    mercury = planets['Mercury']

    # Check conjunction (within 15° — Mercury is always close to Sun)
    orb = abs(sun.longitude - mercury.longitude)
    if orb > 180:
        orb = 360 - orb

    if orb < 15:
        yogas.append(Yoga(
            name='Budhaditya Yoga',
            planets=['Sun', 'Mercury'],
            description=f'Sun-Mercury conjunction ({orb:.1f}°) — intelligence and communication',
            strength='strong' if orb < 5 else 'moderate',
            houses_involved=[sun.house]
        ))

    return yogas


def detect_neechabhanga(planets: dict[str, PlanetPosition], planet_houses_ruled: dict[str, list[int]] = None) -> list[Yoga]:
    """Neechabhanga: Cancellation of debilitation.

    Rules:
    1. Lord of the debilitated sign is in Kendra from Asc or Moon
    2. Lord of exaltation sign of the debilitated planet is in Kendra
    3. The debilitated planet is aspected by its exaltation lord
    """
    yogas = []

    # Debilitation positions (sign index where planet is debilitated)
    debilitation = {
        'Sun': 6,       # Libra
        'Moon': 7,      # Scorpio
        'Mars': 3,      # Cancer
        'Mercury': 11,  # Pisces
        'Jupiter': 5,   # Virgo
        'Venus': 8,     # Sagittarius (some say 11=Pisces)
        'Saturn': 0,    # Aries
    }

    # Exaltation positions
    exaltation = {
        'Sun': 0,       # Aries
        'Moon': 1,      # Taurus
        'Mars': 9,      # Capricorn
        'Mercury': 5,   # Virgo
        'Jupiter': 3,   # Cancer
        'Venus': 11,    # Pisces
        'Saturn': 6,    # Libra
    }

    for pname, p in planets.items():
        if pname in debilitation and p.rashi_index == debilitation[pname]:
            # Planet is debilitated. Check for cancellation.
            # Rule 1: Lord of debilitated sign in Kendra
            deb_sign_lord = RASHI_LORDS[debilitation[pname]]
            if deb_sign_lord in planets:
                lord_pos = planets[deb_sign_lord]
                if lord_pos.house in KENDRA:
                    yogas.append(Yoga(
                        name='Neechabhanga Raja Yoga',
                        planets=[pname, deb_sign_lord],
                        description=f'{pname} debilitation cancelled — {deb_sign_lord} (sign lord) in H{lord_pos.house} (Kendra)',
                        strength='strong',
                        houses_involved=[p.house, lord_pos.house]
                    ))

    return yogas


def detect_pancha_mahapurusha(planets: dict[str, PlanetPosition]) -> list[Yoga]:
    """Pancha Mahapurusha Yoga: Mars/Jupiter/Venus/Saturn/Mercury in own sign in Kendra.

    Creates extraordinary individuals.
    """
    yogas = []

    # Own signs for each planet
    own_signs = {
        'Mars': [0, 7],       # Aries, Scorpio
        'Mercury': [2, 5],    # Gemini, Virgo
        'Jupiter': [8, 11],   # Sagittarius, Pisces
        'Venus': [1, 6],      # Taurus, Libra
        'Saturn': [9, 10],    # Capricorn, Aquarius
    }

    yoga_names = {
        'Mars': 'Ruchaka Yoga',
        'Mercury': 'Bhadra Yoga',
        'Jupiter': 'Hamsa Yoga',
        'Venus': 'Malavya Yoga',
        'Saturn': 'Shasha Yoga',
    }

    for pname, own in own_signs.items():
        if pname in planets:
            p = planets[pname]
            if p.rashi_index in own and p.house in KENDRA:
                yogas.append(Yoga(
                    name=yoga_names[pname],
                    planets=[pname],
                    description=f'{pname} in own sign ({p.rashi}) in Kendra (H{p.house}) — powerful personality',
                    strength='strong',
                    houses_involved=[p.house]
                ))

    return yogas


def detect_chandra_mangala_yoga(planets: dict[str, PlanetPosition]) -> list[Yoga]:
    """Chandra Mangala Yoga: Moon-Mars conjunction.

    Financial acumen, boldness, sometimes aggression.
    """
    yogas = []
    if 'Moon' not in planets or 'Mars' not in planets:
        return yogas

    moon = planets['Moon']
    mars = planets['Mars']

    if moon.rashi_index == mars.rashi_index:
        orb = abs(moon.longitude - mars.longitude)
        if orb > 180:
            orb = 360 - orb
        if orb < 12:
            yogas.append(Yoga(
                name='Chandra Mangala Yoga',
                planets=['Moon', 'Mars'],
                description=f'Moon-Mars conjunction ({orb:.1f}°) — financial boldness',
                strength='strong' if orb < 6 else 'moderate',
                houses_involved=[moon.house]
            ))

    return yogas


def detect_parivartana_yoga(planets: dict[str, PlanetPosition],
                            planet_houses_ruled: dict[str, list[int]] = None) -> list[Yoga]:
    """Parivartana Yoga: two planets occupying each other's signs.

    This detects sign exchange even when the exchange is not purely benefic.
    Subtypes are labeled conservatively:
    - Dainya: any 6/8/12 involvement
    - Khala: otherwise any 3/6/11 involvement
    - Maha: otherwise
    """
    yogas = []
    if not planet_houses_ruled:
        return yogas

    names = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']
    seen: set[tuple[str, str]] = set()

    for name in names:
        if name not in planets:
            continue

        planet = planets[name]
        other_name = get_rashi_lord(planet.rashi_index)
        if other_name == name or other_name not in planets:
            continue

        other = planets[other_name]
        if get_rashi_lord(other.rashi_index) != name:
            continue

        pair = tuple(sorted((name, other_name)))
        if pair in seen:
            continue
        seen.add(pair)

        houses_ruled = sorted(set(planet_houses_ruled.get(name, []) + planet_houses_ruled.get(other_name, [])))
        if any(h in DUSTHANA for h in houses_ruled):
            yoga_name = 'Dainya Parivartana Yoga'
            strength = 'moderate'
        elif any(h in UPACHAYA for h in houses_ruled):
            yoga_name = 'Khala Parivartana Yoga'
            strength = 'moderate'
        else:
            yoga_name = 'Maha Parivartana Yoga'
            strength = 'strong'

        yogas.append(Yoga(
            name=yoga_name,
            planets=[name, other_name],
            description=(
                f'{name} in {planet.rashi} exchanges signs with {other_name} in {other.rashi}. '
                f'This links H{planet.house} and H{other.house} in D1 and ties together the houses they rule '
                f'({", ".join(f"H{h}" for h in houses_ruled)}).'
            ),
            strength=strength,
            houses_involved=sorted(set([planet.house, other.house] + houses_ruled))
        ))

    return yogas


# ===== DETECT ALL =====

def detect_all_yogas(planets: dict[str, PlanetPosition],
                     planet_houses_ruled: dict[str, list[int]] = None) -> list[Yoga]:
    """Run all yoga detectors and return all found yogas."""
    # Auto-calculate house rulerships if not provided
    if not planet_houses_ruled:
        if 'Asc' in planets:
            asc_ri = planets['Asc'].rashi_index
        else:
            # Try to infer from first house planet
            asc_ri = 0
        planet_houses_ruled = calculate_house_rulerships(asc_ri)

    all_yogas = []
    all_yogas.extend(detect_raja_yoga(planets, planet_houses_ruled))
    all_yogas.extend(detect_dhana_yoga(planets, planet_houses_ruled))
    all_yogas.extend(detect_viparita_raja_yoga(planets, planet_houses_ruled))
    all_yogas.extend(detect_gaja_kesari_yoga(planets))
    all_yogas.extend(detect_budhaditya_yoga(planets))
    all_yogas.extend(detect_neechabhanga(planets, planet_houses_ruled))
    all_yogas.extend(detect_pancha_mahapurusha(planets))
    all_yogas.extend(detect_chandra_mangala_yoga(planets))
    all_yogas.extend(detect_parivartana_yoga(planets, planet_houses_ruled))
    return all_yogas


def yoga_to_dict(y: Yoga) -> dict:
    return {
        'name': y.name,
        'planets': y.planets,
        'description': y.description,
        'strength': y.strength,
        'houses': y.houses_involved,
    }
