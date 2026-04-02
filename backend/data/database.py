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
        # Family
        ('Ique (Luiz Bueno)', '1982-03-15', '15:55', 'São Paulo, SP, Brazil', -23.55, -46.63),
        ('Mãe', '1957-10-10', '01:30', 'São Paulo, SP, Brazil', -23.55, -46.63),
        ('Pai', '1953-12-07', '16:00', 'Londrina, Paraná, Brazil', -23.31, -51.17),
        ('Tia Pi', '1958-08-07', '01:10', 'São Paulo, SP, Brazil', -23.55, -46.63),
        ('G', '1960-11-27', '20:00', 'São Paulo, SP, Brazil', -23.55, -46.63),
        ('Primo Andre', '1985-05-09', '17:23', 'São Paulo, SP, Brazil', -23.55, -46.63),
        ('Isa', '2005-02-14', '14:06', 'São Paulo, SP, Brazil', -23.55, -46.63),
        ('Vitor', '2008-08-21', '20:29', 'Ubatuba, SP, Brazil', -23.43, -45.08),
        ('Helena', '2025-02-06', '16:57', 'São Paulo, SP, Brazil', -23.55, -46.63),
        ('Steffany (babá)', '2004-09-26', '14:23', 'São Paulo, SP, Brazil', -23.55, -46.63),
        ('Isa filha Pri', '2013-01-14', '00:30', 'São Paulo, SP, Brazil', -23.55, -46.63),

        # Angela's circle
        ('Angela', '1988-06-15', '04:34', 'Londrina, Paraná, Brazil', -23.31, -51.17),
        ('Gabi Sola', '2019-11-25', '17:47', 'Londrina, Paraná, Brazil', -23.31, -51.17),

        # Friends - Brazil
        ('Fernanda Meireles', '1971-07-05', '10:40', 'São Paulo, SP, Brazil', -23.55, -46.63),
        ('Fernanda Micelli', '1975-09-11', '06:55', 'São Paulo, SP, Brazil', -23.55, -46.63),
        ('Priscila (babá)', '1985-10-31', '12:00', 'São Paulo, SP, Brazil', -23.55, -46.63),
        ('Samantha', '1979-06-08', '18:55', 'Rio Preto, SP, Brazil', -20.81, -49.38),
        ('Maria Clara', '2016-03-09', '07:23', 'Rio Preto, SP, Brazil', -20.81, -49.38),
        ('Fabiao', '1980-11-07', '08:30', 'Rio de Janeiro, Brazil', -22.91, -43.17),
        ('Augusto Weber', '1961-06-25', '07:05', 'Curitiba, Paraná, Brazil', -25.43, -49.27),
        ('Patricia', '1989-06-10', '15:20', 'Belo Horizonte, MG, Brazil', -19.92, -43.94),
        ('Paola Prima', '1966-09-21', '00:40', 'São Paulo, SP, Brazil', -23.55, -46.63),
        ('Claus Riger', '1974-06-15', '04:08', 'São Paulo, SP, Brazil', -23.55, -46.63),
        ('Ricardo Micelli', '1981-10-04', '07:01', 'São Paulo, SP, Brazil', -23.55, -46.63),
        ('Andreia Tersova Rios', '1981-11-18', '17:30', 'Prague, Czech Republic', 50.08, 14.44),
        ('Pedro Paulo Rios', '1982-04-05', '13:05', 'São Paulo, SP, Brazil', -23.55, -46.63),
        ('Laers', '1989-01-06', '10:00', 'Não Me Toque, RS, Brazil', -28.46, -52.82),
        ('Ingrid', '1983-10-24', '11:55', 'São Paulo, SP, Brazil', -23.55, -46.63),

        # Friends - International
        ('Kathrin', '1989-01-14', '06:14', 'Berlin, Germany', 52.52, 13.41),
        ('Nastasia', '1985-01-16', '23:15', 'Tomsk, Russia', 56.50, 84.97),
        ('Marie Hilz', '1997-02-10', '16:29', 'Stade, Germany', 53.59, 9.48),
        ('Alma Hilz', '2017-10-07', '21:15', 'Berlin, Germany', 52.52, 13.41),
        ('Levin', '2020-09-13', '22:03', 'Hamburg, Germany', 53.55, 9.99),
        ('Slawa', '1994-01-25', '12:15', 'Karagandy, Kazakhstan', 49.80, 73.10),
        ('Judith Mohr', '1984-06-25', '20:53', 'Kyritz, Germany', 52.95, 12.38),
        ('Tina', '1990-03-04', '06:53', 'Kiel, Germany', 54.32, 10.12),
        ('Olha Hnenna', '1987-07-06', '08:40', 'Zaporizhzhya, Ukraine', 47.84, 35.14),
    ]

    for name, bdate, btime, place, lat, lon in defaults:
        add_profile(name, bdate, btime, place, lat, lon)


# Initialize on import
init_db()
