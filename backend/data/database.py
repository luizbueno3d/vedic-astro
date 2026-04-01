"""SQLite database for storing birth profiles."""

import sqlite3
import json
from pathlib import Path
from dataclasses import asdict

DB_PATH = Path(__file__).parent.parent / 'data' / 'profiles.db'


def init_db():
    """Initialize the database with required tables."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute('''
        CREATE TABLE IF NOT EXISTS profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            birth_date TEXT NOT NULL,
            birth_time TEXT NOT NULL,
            birth_place TEXT NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            tz_offset REAL DEFAULT -3.0,
            notes TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        )
    ''')
    conn.commit()
    conn.close()


def get_connection() -> sqlite3.Connection:
    """Get a database connection."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def add_profile(name: str, birth_date: str, birth_time: str,
                birth_place: str, latitude: float, longitude: float,
                tz_offset: float = -3.0, notes: str = '') -> int:
    """Add a new birth profile.

    Returns:
        The ID of the new profile
    """
    conn = get_connection()
    cursor = conn.execute('''
        INSERT INTO profiles (name, birth_date, birth_time, birth_place, latitude, longitude, tz_offset, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (name, birth_date, birth_time, birth_place, latitude, longitude, tz_offset, notes))
    conn.commit()
    profile_id = cursor.lastrowid
    conn.close()
    return profile_id


def get_profile(profile_id: int) -> dict | None:
    """Get a profile by ID."""
    conn = get_connection()
    row = conn.execute('SELECT * FROM profiles WHERE id = ?', (profile_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def list_profiles() -> list[dict]:
    """List all profiles."""
    conn = get_connection()
    rows = conn.execute('SELECT * FROM profiles ORDER BY name').fetchall()
    conn.close()
    return [dict(r) for r in rows]


def update_profile(profile_id: int, **kwargs) -> bool:
    """Update a profile's fields."""
    allowed = {'name', 'birth_date', 'birth_time', 'birth_place', 'latitude', 'longitude', 'tz_offset', 'notes'}
    fields = {k: v for k, v in kwargs.items() if k in allowed}
    if not fields:
        return False

    set_clause = ', '.join(f'{k} = ?' for k in fields)
    values = list(fields.values()) + [profile_id]

    conn = get_connection()
    conn.execute(f'UPDATE profiles SET {set_clause}, updated_at = datetime("now") WHERE id = ?', values)
    conn.commit()
    conn.close()
    return True


def delete_profile(profile_id: int) -> bool:
    """Delete a profile."""
    conn = get_connection()
    cursor = conn.execute('DELETE FROM profiles WHERE id = ?', (profile_id,))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted


def seed_default_profiles():
    """Seed the database with default profiles if empty."""
    profiles = list_profiles()
    if profiles:
        return

    defaults = [
        ('Ique (Luiz Bueno)', '1982-03-15', '15:55', 'São Paulo, Brazil', -23.5505, -46.6333),
        ('Angela', '1988-06-15', '04:34', 'Londrina, Paraná, Brazil', -23.31, -51.17),
        ('Helena', '2025-02-06', '16:57', 'São Paulo, Brazil', -23.55, -46.63),
    ]

    for name, bdate, btime, place, lat, lon in defaults:
        add_profile(name, bdate, btime, place, lat, lon)


# Initialize on import
init_db()
