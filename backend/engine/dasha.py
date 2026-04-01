"""Vimshottari Dasha calculation engine."""

from datetime import date, timedelta
from dataclasses import dataclass
from .ephemeris import NAKSHATRAS, NAK_SPAN, get_nakshatra_lord

# Dasha periods in years
DASHA_YEARS = {
    'Ketu': 7, 'Venus': 20, 'Sun': 6, 'Moon': 10,
    'Mars': 7, 'Rahu': 18, 'Jupiter': 16, 'Saturn': 19, 'Mercury': 17
}

DASHA_LORDS = ['Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury']

# Nakshatra to starting dasha mapping
NAK_TO_DASHA = {
    'Ashwini': 'Ketu', 'Bharani': 'Venus', 'Krittika': 'Sun',
    'Rohini': 'Moon', 'Mrigashira': 'Mars', 'Ardra': 'Rahu',
    'Punarvasu': 'Jupiter', 'Pushya': 'Saturn', 'Ashlesha': 'Mercury',
    'Magha': 'Ketu', 'P.Phalguni': 'Venus', 'U.Phalguni': 'Sun',
    'Hasta': 'Moon', 'Chitra': 'Mars', 'Swati': 'Rahu',
    'Vishakha': 'Jupiter', 'Anuradha': 'Saturn', 'Jyeshtha': 'Mercury',
    'Mula': 'Ketu', 'P.Ashadha': 'Venus', 'U.Ashadha': 'Sun',
    'Sravana': 'Moon', 'Dhanishtha': 'Mars', 'Shatabhisha': 'Rahu',
    'P.Bhadrapada': 'Jupiter', 'U.Bhadrapada': 'Saturn', 'Revati': 'Mercury',
}


@dataclass
class DashaPeriod:
    lord: str
    level: str  # 'mahadasha', 'antardasha', 'pratyantardasha'
    start: date
    end: date
    years: float
    is_current: bool = False


def get_starting_dasha(moon_longitude: float) -> tuple[str, float]:
    """Get starting Mahadasha lord and balance from Moon's nakshatra.

    Returns:
        (starting_lord, first_period_years)
    """
    nak_idx = int((moon_longitude % 360) / NAK_SPAN)
    nak_name = NAKSHATRAS[nak_idx]
    starting_lord = NAK_TO_DASHA[nak_name]

    # Calculate balance: portion of nakshatra remaining
    nak_start = nak_idx * NAK_SPAN
    portion_traversed = ((moon_longitude % 360) - nak_start) / NAK_SPAN
    balance = 1.0 - portion_traversed
    first_years = DASHA_YEARS[starting_lord] * balance

    return starting_lord, first_years


def calculate_mahadasha(birth_date: date, moon_longitude: float) -> list[DashaPeriod]:
    """Calculate full Vimshottari Mahadasha timeline.

    Args:
        birth_date: date of birth
        moon_longitude: sidereal Moon longitude

    Returns:
        List of 9 Mahadasha periods
    """
    starting_lord, first_years = get_starting_dasha(moon_longitude)

    # Order dashas starting from the Moon's nakshatra lord
    start_idx = DASHA_LORDS.index(starting_lord)
    ordered = DASHA_LORDS[start_idx:] + DASHA_LORDS[:start_idx]

    today = date.today()
    periods = []
    current_date = birth_date

    for i, lord in enumerate(ordered):
        years = first_years if i == 0 else DASHA_YEARS[lord]
        days = int(years * 365.25)
        end_date = current_date + timedelta(days=days)
        is_current = current_date <= today <= end_date

        periods.append(DashaPeriod(
            lord=lord,
            level='mahadasha',
            start=current_date,
            end=end_date,
            years=years,
            is_current=is_current
        ))
        current_date = end_date

    return periods


def calculate_antardasha(mahadasha: DashaPeriod) -> list[DashaPeriod]:
    """Calculate Antardasha periods within a Mahadasha.

    Args:
        mahadasha: The Mahadasha period

    Returns:
        List of 9 Antardasha periods
    """
    md_lord = mahadasha.lord
    md_years = mahadasha.years

    # Order starts from the Mahadasha lord
    start_idx = DASHA_LORDS.index(md_lord)
    ordered = DASHA_LORDS[start_idx:] + DASHA_LORDS[:start_idx]

    today = date.today()
    periods = []
    current_date = mahadasha.start

    for lord in ordered:
        # Antardasha fraction: (planet_dasha_years / 120) × mahadasha_years
        ad_years = md_years * (DASHA_YEARS[lord] / 120.0)
        days = int(ad_years * 365.25)
        end_date = current_date + timedelta(days=days)
        is_current = current_date <= today <= end_date

        periods.append(DashaPeriod(
            lord=lord,
            level='antardasha',
            start=current_date,
            end=end_date,
            years=ad_years,
            is_current=is_current
        ))
        current_date = end_date
        if current_date > mahadasha.end:
            break

    return periods


def calculate_pratyantardasha(antardasha: DashaPeriod, mahadasha_years: float) -> list[DashaPeriod]:
    """Calculate Pratyantardasha within an Antardasha.

    Args:
        antardasha: The Antardasha period
        mahadasha_years: Duration of the parent Mahadasha

    Returns:
        List of 9 Pratyantardasha periods
    """
    ad_lord = antardasha.lord
    ad_years = antardasha.years

    # Order starts from the Antardasha lord
    start_idx = DASHA_LORDS.index(ad_lord)
    ordered = DASHA_LORDS[start_idx:] + DASHA_LORDS[:start_idx]

    today = date.today()
    periods = []
    current_date = antardasha.start

    for lord in ordered:
        pd_years = ad_years * (DASHA_YEARS[lord] / 120.0)
        days = int(pd_years * 365.25)
        end_date = current_date + timedelta(days=days)
        is_current = current_date <= today <= end_date

        periods.append(DashaPeriod(
            lord=lord,
            level='pratyantardasha',
            start=current_date,
            end=end_date,
            years=pd_years,
            is_current=is_current
        ))
        current_date = end_date
        if current_date > antardasha.end:
            break

    return periods


def get_current_dasha_periods(mahadashas: list[DashaPeriod]) -> dict:
    """Get the current MD, AD, and PD periods."""
    today = date.today()
    result = {'mahadasha': None, 'antardasha': None, 'pratyantardasha': None}

    for md in mahadashas:
        if md.is_current:
            result['mahadasha'] = md
            antardashas = calculate_antardasha(md)
            for ad in antardashas:
                if ad.is_current:
                    result['antardasha'] = ad
                    pratyantardashas = calculate_pratyantardasha(ad, md.years)
                    for pd in pratyantardashas:
                        if pd.is_current:
                            result['pratyantardasha'] = pd
                            break
                    break
            break

    return result


def dasha_to_dict(period: DashaPeriod) -> dict:
    """Serialize a DashaPeriod to a dict."""
    return {
        'lord': period.lord,
        'level': period.level,
        'start': period.start.isoformat(),
        'end': period.end.isoformat(),
        'years': round(period.years, 2),
        'is_current': period.is_current,
    }
