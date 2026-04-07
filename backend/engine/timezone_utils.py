"""Timezone resolution helpers for birth-place selection."""

from datetime import date, datetime
from zoneinfo import ZoneInfo

from timezonefinder import TimezoneFinder

_TF = TimezoneFinder()


def get_timezone_name(lat: float, lon: float) -> str | None:
    """Return IANA timezone name for coordinates."""
    return _TF.timezone_at(lat=lat, lng=lon)


def get_tz_offset_for_date(lat: float, lon: float, target_date: date | None = None) -> dict:
    """Return timezone metadata including offset in hours for a given date."""
    tz_name = get_timezone_name(lat, lon)
    if not tz_name:
        return {'timezone': None, 'tz_offset': None}

    if target_date is None:
        target_date = date.today()

    local_dt = datetime(target_date.year, target_date.month, target_date.day, 12, 0, 0, tzinfo=ZoneInfo(tz_name))
    offset = local_dt.utcoffset()
    hours = offset.total_seconds() / 3600 if offset else 0.0
    return {
        'timezone': tz_name,
        'tz_offset': hours,
    }
