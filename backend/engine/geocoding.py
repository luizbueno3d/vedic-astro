"""Geocoding — look up coordinates from place names.

Uses OpenStreetMap Nominatim (free, no API key needed).
"""

from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable

# Initialize with a user agent (required by Nominatim)
_geocoder = Nominatim(user_agent="vedic-astro-app")


def geocode(place_name: str) -> dict | None:
    """Look up coordinates for a place name.

    Args:
        place_name: City name, e.g. "São Paulo, Brazil"

    Returns:
        dict with 'lat', 'lon', 'display_name', 'tz_offset' or None
    """
    try:
        location = _geocoder.geocode(place_name, exactly_one=True, timeout=5)
        if location:
            # Estimate timezone from longitude
            tz_offset = _estimate_tz(location.longitude, location.latitude)

            return {
                'lat': round(location.latitude, 4),
                'lon': round(location.longitude, 4),
                'display_name': location.address,
                'tz_offset': tz_offset,
            }
    except (GeocoderTimedOut, GeocoderUnavailable):
        pass
    return None


def search_places(query: str, limit: int = 5) -> list[dict]:
    """Search for places matching a query.

    Args:
        query: Partial name, e.g. "São P"
        limit: Max results

    Returns:
        List of dicts with 'name', 'lat', 'lon', 'display_name'
    """
    try:
        results = _geocoder.geocode(query, exactly_one=False, limit=limit, timeout=5)
        if results:
            return [{
                'name': r.address.split(',')[0],
                'display_name': r.address,
                'lat': round(r.latitude, 4),
                'lon': round(r.longitude, 4),
                'tz_offset': _estimate_tz(r.longitude, r.latitude),
            } for r in results]
    except (GeocoderTimedOut, GeocoderUnavailable):
        pass
    return []


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
