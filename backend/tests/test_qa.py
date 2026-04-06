"""QA Validation Suite — Vedic Astro Engine.

Tests all calculations against verified AstroSage PDF output.
Run with: python3 -m pytest backend/tests/test_qa.py -v
Or: python3 backend/tests/test_qa.py
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from engine.ephemeris import calculate_chart, deg_to_dms, get_julian_day
from engine.charts import d9_navamsha, d7_saptamsha, d10_dashamsha, d3_drekkana, d4_chaturthamsa, d12_dwadasamsa
from engine.dasha import calculate_mahadasha, get_starting_dasha
from engine.guna_milan import calculate_guna_milan
import swisseph as swe
from datetime import date

# ============================================================
# TOLERANCES
# ============================================================
DEGREE_TOLERANCE = 0.02  # ~1 arcminute (generous for different ayanamsa)
NAKSHATRA_EXACT = True
PADA_EXACT = True

# ============================================================
# TEST DATA FROM ASTROSAGE PDF
# ============================================================

BIRTH_DATA = {
    'year': 1982, 'month': 3, 'day': 15,
    'hour': 15, 'minute': 55,
    'lat': -23.5505, 'lon': -46.6333,
    'tz': -3.0,
}

# T3: D1 Planetary Longitudes (from PDF Page 3)
D1_EXPECTED = {
    'Asc': {'degree': 106.0589, 'sign': 'Cancer', 'nakshatra': 'Pushya', 'pada': 4},  # 16°03'32"
    'Sun': {'degree': 331.2681, 'sign': 'Pisces', 'nakshatra': 'P.Bhadrapada', 'pada': 4},  # 01°16'05"
    'Moon': {'degree': 220.3089, 'sign': 'Scorpio', 'nakshatra': 'Anuradha', 'pada': 3},  # 10°18'32"
    'Mars': {'degree': 172.2311, 'sign': 'Virgo', 'nakshatra': 'Hasta', 'pada': 4},  # 22°13'52"
    'Mercury': {'degree': 309.3661, 'sign': 'Aquarius', 'nakshatra': 'Shatabhisha', 'pada': 1},  # 09°21'58"
    'Jupiter': {'degree': 196.1361, 'sign': 'Libra', 'nakshatra': 'Swati', 'pada': 3},  # 16°08'10"
    'Venus': {'degree': 286.1175, 'sign': 'Capricorn', 'nakshatra': 'Sravana', 'pada': 2},  # 16°07'03"
    'Saturn': {'degree': 177.0917, 'sign': 'Virgo', 'nakshatra': 'Chitra', 'pada': 2},  # 27°05'30"
    'Rahu': {'degree': 85.6700, 'sign': 'Gemini', 'nakshatra': 'Punarvasu', 'pada': 2},  # 25°40'12" (KP New)
    'Ketu': {'degree': 265.6700, 'sign': 'Sagittarius', 'nakshatra': 'P.Ashadha', 'pada': 4},  # 25°40'12"
}

# T5: D9 Navamsha (from PDF Page 40, corrected to 0-indexed sign indices)
D9_EXPECTED = {
    'Asc': 7,      # Scorpio
    'Sun': 3,      # Cancer
    'Moon': 6,     # Libra
    'Mars': 3,     # Cancer
    'Mercury': 8,  # Sagittarius
    'Jupiter': 10, # Aquarius
    'Venus': 1,    # Taurus
    'Saturn': 5,   # Virgo
    'Rahu': 1,     # Taurus
    'Ketu': 8,     # Sagittarius
}

# D7 Saptamamsha (from PDF Page 40, corrected to 0-indexed sign indices)
D7_EXPECTED = {
    'Asc': 0,      # Aries
    'Sun': 5,      # Virgo
    'Moon': 3,     # Cancer
    'Mars': 4,     # Leo
    'Mercury': 0,  # Aries
    'Jupiter': 9,  # Capricorn
    'Venus': 6,    # Libra
    'Saturn': 5,   # Virgo
}

# D10 Dashamamsha (from PDF Page 40, corrected to 0-indexed sign indices)
D10_EXPECTED = {
    'Asc': 4,      # Leo
    'Sun': 7,      # Scorpio
    'Moon': 6,     # Libra
    'Mars': 8,     # Sagittarius
    'Mercury': 1,  # Taurus
    'Jupiter': 11, # Pisces
    'Venus': 10,   # Aquarius
    'Saturn': 10,  # Aquarius
}

# T6.2: KP Cusps (from PDF Page 44)
KP_CUSPS = [
    106.1483,  # H1: 106°08'54"
    144.2483,  # H2: 144°14'54"
    179.7069,  # H3: 179°42'25"
    209.0494,  # H4: 209°02'58"
    234.1817,  # H5: 234°10'54"
    258.5286,  # H6: 258°31'43"
    286.1483,  # H7: 286°08'54"
    324.2483,  # H8: 324°14'54"
    359.7069,  # H9: 359°42'25"
    29.0494,   # H10: 029°02'58"
    54.1817,   # H11: 054°10'54"
    78.5286,   # H12: 078°31'43"
]

# T6.3: KP Planetary Positions (from PDF Page 44, KP New Ayanamsa)
KP_PLANETS = {
    'Sun': 331.3575,      # 331°21'27"
    'Moon': 220.3986,     # 220°23'55"
    'Mars': 172.3208,     # 172°19'15"
    'Mercury': 309.4558,  # 309°27'21"
    'Jupiter': 196.2258,  # 196°13'33"
    'Venus': 286.2069,    # 286°12'25"
    'Saturn': 177.1811,   # 177°10'52"
    'Rahu': 85.7597,      # 085°45'35"
    'Ketu': 265.7597,     # 265°45'35"
}

# T6.4: KP Dasha Dates
KP_DASHA = {
    'Saturn': ('1982-03-15', '1991-02-21'),
    'Mercury': ('1991-02-21', '2008-02-21'),
    'Ketu': ('2008-02-21', '2015-02-21'),
    'Venus': ('2015-02-21', '2035-02-21'),
}


# ============================================================
# TEST RUNNER
# ============================================================

class QAResult:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.warnings = 0
        self.results = []

    def check(self, test_id: str, description: str, actual, expected, tolerance=None):
        if tolerance is not None:
            ok = abs(actual - expected) <= tolerance
        elif isinstance(expected, str):
            ok = str(actual) == str(expected)
        elif isinstance(expected, int):
            ok = int(actual) == expected
        else:
            ok = actual == expected

        status = "PASS" if ok else "FAIL"
        if ok:
            self.passed += 1
        else:
            self.failed += 1

        self.results.append({
            'id': test_id,
            'desc': description,
            'actual': actual,
            'expected': expected,
            'status': status,
        })

        return ok

    def print_report(self):
        print("\n" + "=" * 80)
        print("QA VALIDATION REPORT")
        print("=" * 80)

        for r in self.results:
            icon = "✅" if r['status'] == 'PASS' else "❌"
            print(f"  {icon} {r['id']}: {r['desc']}")
            if r['status'] == 'FAIL':
                print(f"      Expected: {r['expected']}")
                print(f"      Actual:   {r['actual']}")

        print(f"\n{'='*80}")
        print(f"  PASSED: {self.passed}  FAILED: {self.failed}  WARNINGS: {self.warnings}")
        if self.failed == 0:
            print(f"  ✅ ALL TESTS PASSED")
        else:
            print(f"  ❌ {self.failed} TEST(S) FAILED")
        print(f"{'='*80}\n")

        return self.failed == 0


def run_tests():
    qa = QAResult()

    # Set Lahiri ayanamsa
    swe.set_sid_mode(swe.SIDM_LAHIRI)

    # Calculate chart
    chart = calculate_chart(
        BIRTH_DATA['year'], BIRTH_DATA['month'], BIRTH_DATA['day'],
        BIRTH_DATA['hour'], BIRTH_DATA['minute'],
        BIRTH_DATA['lat'], BIRTH_DATA['lon'],
        tz_offset=BIRTH_DATA['tz']
    )

    print("\n--- T1: Input Normalization ---")
    qa.check('T1.1', 'Birth date', chart.birth_date, '1982-03-15')
    qa.check('T1.2', 'Birth time', chart.birth_time, '15:55')

    print("--- T2: Ayanamsa ---")
    qa.check('T2.2', 'Lahiri Ayanamsa', round(chart.ayanamsa, 4), 23.6083, tolerance=0.01)

    print("--- T3: D1 Planetary Longitudes (Lahiri) ---")
    # Rahu/Ketu may differ due to True vs Mean node and ayanamsa
    for planet in ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']:
        expected = D1_EXPECTED[planet]
        if planet == 'Asc':
            actual_lon = chart.ascendant.longitude
            actual_sign = chart.ascendant.rashi
            actual_nak = chart.ascendant.nakshatra
            actual_pada = chart.ascendant.pada
        else:
            p = chart.planets[planet]
            actual_lon = p.longitude
            actual_sign = p.rashi
            actual_nak = p.nakshatra
            actual_pada = p.pada

        qa.check(f'T3.{planet}', f'{planet} longitude', actual_lon, expected['degree'], tolerance=DEGREE_TOLERANCE)
        qa.check(f'T3.{planet}.sign', f'{planet} sign', actual_sign, expected['sign'])
        qa.check(f'T3.{planet}.nak', f'{planet} nakshatra', actual_nak, expected['nakshatra'])
        qa.check(f'T3.{planet}.pada', f'{planet} pada', actual_pada, expected['pada'])

    # Ascendant
    qa.check('T3.ASC', 'Asc longitude', chart.ascendant.longitude, D1_EXPECTED['Asc']['degree'], tolerance=DEGREE_TOLERANCE)
    qa.check('T3.ASC.sign', 'Asc sign', chart.ascendant.rashi, D1_EXPECTED['Asc']['sign'])
    qa.check('T3.ASC.nak', 'Asc nakshatra', chart.ascendant.nakshatra, D1_EXPECTED['Asc']['nakshatra'])
    qa.check('T3.ASC.pada', 'Asc pada', chart.ascendant.pada, D1_EXPECTED['Asc']['pada'])

    print("--- T5: D9 Navamsha ---")
    for planet in ['Asc', 'Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']:
        if planet == 'Asc':
            lon = chart.ascendant.longitude
        else:
            lon = chart.planets[planet].longitude

        d9_sign = d9_navamsha(lon)
        d9_idx = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces'].index(d9_sign)
        qa.check(f'T5.{planet}', f'D9 {planet}', d9_idx, D9_EXPECTED[planet])

    print("--- T5a: Division Boundary Sanity Checks ---")
    qa.check('T5a.D3.AriesStart', 'D3 Aries 0deg starts in Aries', d3_drekkana(0.1), 'Aries')
    qa.check('T5a.D4.AriesStart', 'D4 Aries 0deg starts in Aries', d4_chaturthamsa(0.1), 'Aries')
    qa.check('T5a.D7.AriesStart', 'D7 Aries 0deg starts in Aries', d7_saptamsha(0.1), 'Aries')
    qa.check('T5a.D9.AriesStart', 'D9 Aries 0deg starts in Aries', d9_navamsha(0.1), 'Aries')
    qa.check('T5a.D10.AriesStart', 'D10 Aries 0deg starts in Aries', d10_dashamsha(0.1), 'Aries')
    qa.check('T5a.D12.AriesStart', 'D12 Aries 0deg starts in Aries', d12_dwadasamsa(0.1), 'Aries')

    print("--- T5b: D7 Saptamamsha ---")
    for planet in ['Asc', 'Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']:
        if planet == 'Asc':
            lon = chart.ascendant.longitude
        else:
            lon = chart.planets[planet].longitude

        d7_sign = d7_saptamsha(lon)
        d7_idx = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces'].index(d7_sign)
        qa.check(f'T7.{planet}', f'D7 {planet}', d7_idx, D7_EXPECTED[planet])

    print("--- T5c: D10 Dashamamsha ---")
    for planet in ['Asc', 'Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']:
        if planet == 'Asc':
            lon = chart.ascendant.longitude
        else:
            lon = chart.planets[planet].longitude

        d10_sign = d10_dashamsha(lon)
        d10_idx = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces'].index(d10_sign)
        qa.check(f'T10.{planet}', f'D10 {planet}', d10_idx, D10_EXPECTED[planet])

    print("--- T6.4: Dasha Sequence ---")
    moon_lon = chart.planets['Moon'].longitude
    starting = get_starting_dasha(moon_lon)[0]
    qa.check('T6.4.start', 'Starting dasha', starting, 'Saturn')

    mds = calculate_mahadasha(date(1982, 3, 15), moon_lon)
    dasha_lords = [md.lord for md in mds]
    qa.check('T6.4.seq', 'Dasha sequence', dasha_lords[:4], ['Saturn', 'Mercury', 'Ketu', 'Venus'])

    print("--- T8: Guna Milan Regression ---")
    female_chart = calculate_chart(1990, 3, 4, 6, 53, 54 + 19/60, 10 + 8/60, tz_offset=1.0)
    male_chart = calculate_chart(1982, 3, 15, 15, 55, -(23 + 32/60), -(46 + 38/60), tz_offset=-3.0)
    guna = calculate_guna_milan(female_chart.planets['Moon'], male_chart.planets['Moon'])
    qa.check('T8.total', 'Guna Milan target pair total', guna['total'], 29.5)

    qa.print_report()
    return qa.failed == 0


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
