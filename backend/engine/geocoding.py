"""Geocoding — look up coordinates from place names.

Uses OpenStreetMap Nominatim (free, no API key needed).
Falls back to direct HTTP if geopy SSL fails.
"""

import requests

from .timezone_utils import get_tz_offset_for_date

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"


def search_places(query: str, limit: int = 5) -> list[dict]:
    """Search for places matching a query."""
    try:
        resp = requests.get(NOMINATIM_URL, params={
            'q': query, 'format': 'json', 'limit': limit,
            'addressdetails': 1,
        }, headers={'User-Agent': 'vedic-astro-app'}, timeout=10, verify=True)
        results = resp.json()
        return [{
            'name': r.get('display_name', '').split(',')[0],
            'display_name': r.get('display_name', ''),
            'lat': round(float(r['lat']), 4),
            'lon': round(float(r['lon']), 4),
            'tz_offset': get_tz_offset_for_date(float(r['lat']), float(r['lon']))['tz_offset'] or _estimate_tz(float(r['lon']), float(r['lat'])),
        } for r in results]
    except Exception:
        # Fallback: try without SSL verification
        try:
            resp = requests.get(NOMINATIM_URL, params={
                'q': query, 'format': 'json', 'limit': limit,
            }, headers={'User-Agent': 'vedic-astro-app'}, timeout=10, verify=False)
            results = resp.json()
            return [{
                'name': r.get('display_name', '').split(',')[0],
                'display_name': r.get('display_name', ''),
                'lat': round(float(r['lat']), 4),
                'lon': round(float(r['lon']), 4),
                'tz_offset': get_tz_offset_for_date(float(r['lat']), float(r['lon']))['tz_offset'] or _estimate_tz(float(r['lon']), float(r['lat'])),
            } for r in results]
        except Exception:
            return []


def geocode(place_name: str) -> dict | None:
    """Look up coordinates for a place name."""
    results = search_places(place_name, limit=1)
    return results[0] if results else None


def _estimate_tz(lon: float, lat: float) -> float:
    """Estimate timezone offset from longitude.

    This is a rough estimate. For exact timezone, use a timezone database.
    """
    # Basic: longitude / 15 = hours from UTC
    # Rounded to nearest 0.5
    import math
    tz = round(lon / 15 * 2) / 2

    # Brazil special case
    if -35 < lon < -34 and -10 < lat < 0:
        return -2.0  # Fernando de Noronha
    if -75 < lon < -35 and -35 < lat < 5:
        return -3.0  # Mainland Brazil (BRT)
    if -75 < lon < -35 and -55 < lat < -35:
        return -3.0  # Southern Brazil

    # India special case
    if 68 < lon < 98 and 6 < lat < 36:
        return 5.5

    return tz
