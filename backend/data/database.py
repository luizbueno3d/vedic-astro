"""SQLite database for storing birth profiles."""

import json
import sqlite3
import os
from pathlib import Path

_DEFAULT_DB_PATH = Path(__file__).parent.parent / 'data' / 'profiles.db'
DB_PATH = Path(os.getenv('VEDIC_ASTRO_DB_PATH', str(_DEFAULT_DB_PATH)))
DEFAULT_OWNER_EMAIL = os.getenv('DEFAULT_OWNER_EMAIL', 'luizbueno3d@gmail.com')
DEFAULT_READING_PRODUCT_CODE = 'life_map'
DEFAULT_READING_TEMPLATE_VERSION = 'life_map_v1'


class CommercialOrderError(ValueError):
    """Expected commercial-order workflow error."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


def init_db():
    """Initialize the database with required tables."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute('PRAGMA foreign_keys = ON')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            owner_email TEXT,
            owner_uid TEXT,
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
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            firebase_uid TEXT UNIQUE,
            email TEXT UNIQUE NOT NULL,
            display_name TEXT,
            locale TEXT DEFAULT 'en',
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now')),
            last_login_at TEXT
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS user_ai_settings (
            owner_email TEXT PRIMARY KEY,
            config_json TEXT NOT NULL,
            updated_at TEXT DEFAULT (datetime('now'))
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS reading_products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            active INTEGER NOT NULL DEFAULT 1 CHECK (active IN (0, 1)),
            title_key TEXT NOT NULL,
            description_key TEXT NOT NULL,
            base_price_cents INTEGER NOT NULL,
            currency TEXT NOT NULL DEFAULT 'BRL',
            template_version TEXT NOT NULL,
            metadata_json TEXT NOT NULL DEFAULT '{}',
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS reading_orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            owner_email TEXT NOT NULL,
            profile_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            locale TEXT NOT NULL DEFAULT 'en',
            status TEXT NOT NULL DEFAULT 'pending_payment'
                CHECK (status IN ('pending_payment', 'paid', 'generating', 'complete', 'failed', 'cancelled', 'refunded')),
            price_cents INTEGER NOT NULL,
            currency TEXT NOT NULL DEFAULT 'BRL',
            campaign_tier TEXT,
            payment_provider TEXT DEFAULT 'stripe',
            stripe_checkout_session_id TEXT UNIQUE,
            stripe_checkout_url TEXT,
            stripe_checkout_expires_at INTEGER,
            stripe_payment_intent_id TEXT,
            stripe_customer_id TEXT,
            paid_at TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(profile_id) REFERENCES profiles(id),
            FOREIGN KEY(product_id) REFERENCES reading_products(id)
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS generated_readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER UNIQUE NOT NULL,
            locale TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending'
                CHECK (status IN ('pending', 'generating', 'complete', 'failed')),
            profile_snapshot_json TEXT NOT NULL DEFAULT '{}',
            calculation_snapshot_json TEXT NOT NULL DEFAULT '{}',
            jaimini_snapshot_json TEXT NOT NULL DEFAULT '{}',
            content_json TEXT NOT NULL DEFAULT '{}',
            content_markdown TEXT,
            model_provider TEXT,
            model_name TEXT,
            template_version TEXT NOT NULL,
            error_message TEXT,
            generated_at TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY(order_id) REFERENCES reading_orders(id)
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS reading_exports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reading_id INTEGER NOT NULL,
            format TEXT NOT NULL DEFAULT 'pdf'
                CHECK (format IN ('pdf', 'markdown', 'txt', 'json')),
            file_path TEXT,
            content_type TEXT,
            checksum TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY(reading_id) REFERENCES generated_readings(id),
            UNIQUE(reading_id, format)
        )
    ''')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_reading_orders_owner_email ON reading_orders(owner_email)')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_reading_orders_profile_id ON reading_orders(profile_id)')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_reading_orders_status ON reading_orders(status)')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_reading_orders_stripe_session ON reading_orders(stripe_checkout_session_id)')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_generated_readings_order_id ON generated_readings(order_id)')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_reading_exports_reading_id ON reading_exports(reading_id)')
    _ensure_profile_ownership_columns(conn)
    _ensure_reading_order_stripe_columns(conn)
    seed_reading_products(conn)
    conn.commit()
    conn.close()


def _ensure_profile_ownership_columns(conn: sqlite3.Connection):
    columns = {row[1] for row in conn.execute('PRAGMA table_info(profiles)').fetchall()}
    if 'owner_email' not in columns:
        conn.execute('ALTER TABLE profiles ADD COLUMN owner_email TEXT')
    if 'owner_uid' not in columns:
        conn.execute('ALTER TABLE profiles ADD COLUMN owner_uid TEXT')
    conn.execute('UPDATE profiles SET owner_email = ? WHERE owner_email IS NULL OR owner_email = ""', (DEFAULT_OWNER_EMAIL,))


def _ensure_reading_order_stripe_columns(conn: sqlite3.Connection):
    columns = {row[1] for row in conn.execute('PRAGMA table_info(reading_orders)').fetchall()}
    if 'stripe_checkout_url' not in columns:
        conn.execute('ALTER TABLE reading_orders ADD COLUMN stripe_checkout_url TEXT')
    if 'stripe_checkout_expires_at' not in columns:
        conn.execute('ALTER TABLE reading_orders ADD COLUMN stripe_checkout_expires_at INTEGER')


def get_connection() -> sqlite3.Connection:
    """Get a database connection."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute('PRAGMA foreign_keys = ON')
    conn.row_factory = sqlite3.Row
    return conn


def seed_reading_products(conn: sqlite3.Connection | None = None):
    """Seed commercial reading products without overwriting production edits."""
    should_close = conn is None
    conn = conn or get_connection()
    conn.execute(
        '''
        INSERT INTO reading_products (
            code, active, title_key, description_key,
            base_price_cents, currency, template_version, metadata_json
        )
        VALUES (?, 1, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(code) DO NOTHING
        ''',
        (
            DEFAULT_READING_PRODUCT_CODE,
            'products.life_map.title',
            'products.life_map.description',
            9999,
            'BRL',
            DEFAULT_READING_TEMPLATE_VERSION,
            json.dumps({
                'english_name': 'Life Map Reading',
                'portuguese_name': 'Mapa de Vida Védico',
                'campaign': {
                    'first_100_price_cents': 1099,
                    'next_100_price_cents': 5999,
                    'standard_price_cents': 9999,
                },
            }),
        ),
    )
    if should_close:
        conn.commit()
        conn.close()


def list_reading_products(active_only: bool = True) -> list[dict]:
    """List commercial reading products."""
    conn = get_connection()
    query = 'SELECT * FROM reading_products'
    params: tuple = ()
    if active_only:
        query += ' WHERE active = ?'
        params = (1,)
    query += ' ORDER BY id'
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_reading_product(code: str) -> dict | None:
    """Get one commercial reading product by stable code."""
    conn = get_connection()
    row = conn.execute('SELECT * FROM reading_products WHERE code = ?', (code,)).fetchone()
    conn.close()
    return dict(row) if row else None


def ensure_user(email: str, firebase_uid: str | None = None,
                display_name: str | None = None, locale: str = 'en') -> dict:
    """Create or update a user row for commercial ownership joins."""
    conn = get_connection()
    row = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
    if row:
        conn.execute(
            '''
            UPDATE users
            SET firebase_uid = COALESCE(NULLIF(?, ''), firebase_uid),
                display_name = COALESCE(NULLIF(?, ''), display_name),
                locale = COALESCE(NULLIF(?, ''), locale),
                last_login_at = datetime('now'),
                updated_at = datetime('now')
            WHERE email = ?
            ''',
            (firebase_uid or '', display_name or '', locale or '', email),
        )
    else:
        conn.execute(
            '''
            INSERT INTO users (firebase_uid, email, display_name, locale, last_login_at)
            VALUES (?, ?, ?, ?, datetime('now'))
            ''',
            (firebase_uid, email, display_name, locale),
        )
    conn.commit()
    user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
    conn.close()
    return dict(user)


def _metadata(row: sqlite3.Row | dict) -> dict:
    try:
        return json.loads(row['metadata_json'] or '{}')
    except Exception:
        return {}


def _campaign_price_for_product(conn: sqlite3.Connection, product: sqlite3.Row | dict) -> dict:
    """Return server-side campaign price for a product."""
    paid_count = conn.execute(
        '''
        SELECT COUNT(*)
        FROM reading_orders
        WHERE product_id = ?
          AND (
            paid_at IS NOT NULL
            OR (status = 'pending_payment' AND stripe_checkout_session_id IS NOT NULL)
          )
        ''',
        (product['id'],),
    ).fetchone()[0]

    campaign = _metadata(product).get('campaign', {})
    if paid_count < 100:
        return {
            'price_cents': int(campaign.get('first_100_price_cents', product['base_price_cents'])),
            'campaign_tier': 'first_100',
            'paid_count_before_order': paid_count,
        }
    if paid_count < 200:
        return {
            'price_cents': int(campaign.get('next_100_price_cents', product['base_price_cents'])),
            'campaign_tier': 'next_100',
            'paid_count_before_order': paid_count,
        }
    return {
        'price_cents': int(campaign.get('standard_price_cents', product['base_price_cents'])),
        'campaign_tier': 'standard',
        'paid_count_before_order': paid_count,
    }


def _order_with_product(conn: sqlite3.Connection, where_sql: str, params: tuple) -> dict | None:
    row = conn.execute(
        f'''
        SELECT ro.*, rp.code AS product_code, rp.title_key, rp.description_key, rp.template_version
        FROM reading_orders ro
        JOIN reading_products rp ON rp.id = ro.product_id
        WHERE {where_sql}
        ''',
        params,
    ).fetchone()
    return dict(row) if row else None


def create_reading_order(owner_email: str, profile_id: int,
                         product_code: str = DEFAULT_READING_PRODUCT_CODE,
                         locale: str = 'en', user_id: int | None = None) -> dict:
    """Create a pending-payment reading order using server-side pricing."""
    conn = get_connection()
    profile = conn.execute(
        'SELECT id FROM profiles WHERE id = ? AND owner_email = ?',
        (profile_id, owner_email),
    ).fetchone()
    if not profile:
        conn.close()
        raise CommercialOrderError('profile_not_found', 'Profile not found for this account')

    product = conn.execute(
        'SELECT * FROM reading_products WHERE code = ? AND active = 1',
        (product_code,),
    ).fetchone()
    if not product:
        conn.close()
        raise CommercialOrderError('product_not_found', 'Reading product not found')

    price = _campaign_price_for_product(conn, product)
    cursor = conn.execute(
        '''
        INSERT INTO reading_orders (
            user_id, owner_email, profile_id, product_id, locale,
            status, price_cents, currency, campaign_tier, payment_provider
        )
        VALUES (?, ?, ?, ?, ?, 'pending_payment', ?, ?, ?, 'stripe')
        ''',
        (
            user_id,
            owner_email,
            profile_id,
            product['id'],
            locale,
            price['price_cents'],
            product['currency'],
            price['campaign_tier'],
        ),
    )
    conn.commit()
    order_id = int(cursor.lastrowid or 0)
    row = _order_with_product(conn, 'ro.id = ?', (order_id,))
    conn.close()
    return row


def list_reading_orders(owner_email: str) -> list[dict]:
    """List commercial reading orders for one owner."""
    conn = get_connection()
    rows = conn.execute(
        '''
        SELECT ro.*, rp.code AS product_code, rp.title_key, rp.description_key, rp.template_version
        FROM reading_orders ro
        JOIN reading_products rp ON rp.id = ro.product_id
        WHERE ro.owner_email = ?
        ORDER BY ro.created_at DESC, ro.id DESC
        ''',
        (owner_email,),
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_reading_order(order_id: int, owner_email: str) -> dict | None:
    """Get a commercial reading order by owner."""
    conn = get_connection()
    row = _order_with_product(conn, 'ro.id = ? AND ro.owner_email = ?', (order_id, owner_email))
    conn.close()
    return row


def get_reading_order_by_stripe_session(stripe_checkout_session_id: str) -> dict | None:
    """Get a commercial reading order by Stripe Checkout Session id."""
    conn = get_connection()
    row = _order_with_product(
        conn,
        'ro.stripe_checkout_session_id = ?',
        (stripe_checkout_session_id,),
    )
    conn.close()
    return row


def prepare_order_for_checkout(order_id: int, owner_email: str) -> dict:
    """Reserve the current campaign price immediately before creating Checkout."""
    conn = get_connection()
    order = conn.execute(
        'SELECT * FROM reading_orders WHERE id = ? AND owner_email = ?',
        (order_id, owner_email),
    ).fetchone()
    if not order:
        conn.close()
        raise CommercialOrderError('order_not_found', 'Reading order not found')
    if order['status'] != 'pending_payment':
        conn.close()
        raise CommercialOrderError('invalid_order_state', 'Only pending-payment orders can start checkout')
    if order['stripe_checkout_session_id'] and order['stripe_checkout_url']:
        row = _order_with_product(conn, 'ro.id = ?', (order_id,))
        conn.close()
        return row
    if order['stripe_checkout_session_id']:
        conn.close()
        raise CommercialOrderError('checkout_exists', 'Checkout already exists for this order')

    product = conn.execute(
        'SELECT * FROM reading_products WHERE id = ? AND active = 1',
        (order['product_id'],),
    ).fetchone()
    if not product:
        conn.close()
        raise CommercialOrderError('product_not_found', 'Reading product not found')

    price = _campaign_price_for_product(conn, product)
    conn.execute(
        '''
        UPDATE reading_orders
        SET price_cents = ?, currency = ?, campaign_tier = ?, updated_at = datetime('now')
        WHERE id = ?
        ''',
        (price['price_cents'], product['currency'], price['campaign_tier'], order_id),
    )
    conn.commit()
    row = _order_with_product(conn, 'ro.id = ?', (order_id,))
    conn.close()
    return row


def attach_stripe_checkout_session(order_id: int, owner_email: str, session_id: str,
                                   checkout_url: str, expires_at: int | None = None) -> dict:
    """Attach a Stripe Checkout Session to a pending owner-scoped order."""
    conn = get_connection()
    order = conn.execute(
        'SELECT * FROM reading_orders WHERE id = ? AND owner_email = ?',
        (order_id, owner_email),
    ).fetchone()
    if not order:
        conn.close()
        raise CommercialOrderError('order_not_found', 'Reading order not found')
    if order['status'] != 'pending_payment':
        conn.close()
        raise CommercialOrderError('invalid_order_state', 'Only pending-payment orders can attach checkout')
    if order['stripe_checkout_session_id'] and order['stripe_checkout_session_id'] != session_id:
        conn.close()
        raise CommercialOrderError('checkout_exists', 'Checkout already exists for this order')

    conn.execute(
        '''
        UPDATE reading_orders
        SET stripe_checkout_session_id = ?,
            stripe_checkout_url = ?,
            stripe_checkout_expires_at = ?,
            updated_at = datetime('now')
        WHERE id = ?
        ''',
        (session_id, checkout_url, expires_at, order_id),
    )
    conn.commit()
    row = _order_with_product(conn, 'ro.id = ?', (order_id,))
    conn.close()
    return row


def mark_order_paid_from_stripe(stripe_checkout_session_id: str,
                                payment_intent_id: str | None = None,
                                customer_id: str | None = None,
                                amount_total: int | None = None,
                                currency: str | None = None) -> dict:
    """Idempotently mark a Stripe Checkout order as paid after verified webhook."""
    conn = get_connection()
    order = conn.execute(
        'SELECT * FROM reading_orders WHERE stripe_checkout_session_id = ?',
        (stripe_checkout_session_id,),
    ).fetchone()
    if not order:
        conn.close()
        raise CommercialOrderError('order_not_found', 'Reading order not found for Stripe session')
    if amount_total is not None and int(amount_total) != int(order['price_cents']):
        conn.close()
        raise CommercialOrderError('payment_amount_mismatch', 'Stripe amount does not match server-side order price')
    if currency and currency.upper() != str(order['currency']).upper():
        conn.close()
        raise CommercialOrderError('payment_currency_mismatch', 'Stripe currency does not match server-side order currency')
    if order['status'] in {'cancelled', 'refunded'}:
        conn.close()
        raise CommercialOrderError('invalid_order_state', 'Cancelled or refunded orders cannot be marked paid')

    next_status = order['status']
    if order['status'] == 'pending_payment':
        next_status = 'paid'

    conn.execute(
        '''
        UPDATE reading_orders
        SET status = ?,
            stripe_payment_intent_id = COALESCE(NULLIF(?, ''), stripe_payment_intent_id),
            stripe_customer_id = COALESCE(NULLIF(?, ''), stripe_customer_id),
            paid_at = COALESCE(paid_at, datetime('now')),
            updated_at = datetime('now')
        WHERE id = ?
        ''',
        (next_status, payment_intent_id or '', customer_id or '', order['id']),
    )
    conn.commit()
    row = _order_with_product(conn, 'ro.id = ?', (order['id'],))
    conn.close()
    return row


def cancel_order_from_stripe_session(stripe_checkout_session_id: str) -> dict | None:
    """Cancel a pending order when Stripe reports the Checkout Session expired."""
    conn = get_connection()
    order = conn.execute(
        'SELECT * FROM reading_orders WHERE stripe_checkout_session_id = ?',
        (stripe_checkout_session_id,),
    ).fetchone()
    if not order:
        conn.close()
        return None
    if order['status'] == 'pending_payment':
        conn.execute(
            '''
            UPDATE reading_orders
            SET status = 'cancelled', updated_at = datetime('now')
            WHERE id = ?
            ''',
            (order['id'],),
        )
        conn.commit()
    row = _order_with_product(conn, 'ro.id = ?', (order['id'],))
    conn.close()
    return row


def get_generated_reading_for_order(order_id: int, owner_email: str) -> dict | None:
    """Get generated reading content for an owner-scoped order."""
    conn = get_connection()
    row = conn.execute(
        '''
        SELECT gr.*
        FROM generated_readings gr
        JOIN reading_orders ro ON ro.id = gr.order_id
        WHERE gr.order_id = ? AND ro.owner_email = ?
        ''',
        (order_id, owner_email),
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def order_can_generate(order: dict | None) -> bool:
    """Only paid orders can create a generated reading."""
    return bool(order and order.get('status') == 'paid')


def store_generated_reading_for_order(order_id: int, owner_email: str, snapshot: dict,
                                      model_provider: str = 'deterministic',
                                      model_name: str = 'life_map_snapshot') -> dict:
    """Persist a generated reading snapshot for a paid owner-scoped order."""
    conn = get_connection()
    order = conn.execute(
        'SELECT * FROM reading_orders WHERE id = ? AND owner_email = ?',
        (order_id, owner_email),
    ).fetchone()
    if not order:
        conn.close()
        raise CommercialOrderError('order_not_found', 'Reading order not found')
    if order['status'] == 'complete':
        existing = conn.execute(
            'SELECT * FROM generated_readings WHERE order_id = ?',
            (order_id,),
        ).fetchone()
        conn.close()
        if existing:
            return dict(existing)
        raise CommercialOrderError('missing_generated_reading', 'Order is complete but generated reading is missing')
    if order['status'] != 'paid':
        conn.close()
        raise CommercialOrderError('payment_required', 'Order must be paid before generation')
    if snapshot.get('locale') != order['locale']:
        conn.close()
        raise CommercialOrderError('locale_mismatch', 'Generated reading locale must match order locale')

    conn.execute(
        'UPDATE reading_orders SET status = ?, updated_at = datetime("now") WHERE id = ?',
        ('generating', order_id),
    )
    conn.execute(
        '''
        INSERT INTO generated_readings (
            order_id, locale, status, profile_snapshot_json,
            calculation_snapshot_json, jaimini_snapshot_json, content_json,
            content_markdown, model_provider, model_name, template_version,
            generated_at, updated_at
        )
        VALUES (?, ?, 'complete', ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
        ON CONFLICT(order_id) DO UPDATE SET
            locale = excluded.locale,
            status = excluded.status,
            profile_snapshot_json = excluded.profile_snapshot_json,
            calculation_snapshot_json = excluded.calculation_snapshot_json,
            jaimini_snapshot_json = excluded.jaimini_snapshot_json,
            content_json = excluded.content_json,
            content_markdown = excluded.content_markdown,
            model_provider = excluded.model_provider,
            model_name = excluded.model_name,
            template_version = excluded.template_version,
            error_message = NULL,
            generated_at = datetime('now'),
            updated_at = datetime('now')
        ''',
        (
            order_id,
            snapshot['locale'],
            json.dumps(snapshot['profile_snapshot'], ensure_ascii=False),
            json.dumps(snapshot['calculation_snapshot'], ensure_ascii=False),
            json.dumps(snapshot['jaimini_snapshot'], ensure_ascii=False),
            json.dumps(snapshot['content_json'], ensure_ascii=False),
            snapshot['content_markdown'],
            model_provider,
            model_name,
            snapshot['template_version'],
        ),
    )
    conn.execute(
        'UPDATE reading_orders SET status = ?, updated_at = datetime("now") WHERE id = ?',
        ('complete', order_id),
    )
    conn.commit()
    row = conn.execute('SELECT * FROM generated_readings WHERE order_id = ?', (order_id,)).fetchone()
    conn.close()
    return dict(row)


def add_profile(name: str, birth_date: str, birth_time: str,
                birth_place: str, latitude: float, longitude: float,
                tz_offset: float = -3.0, notes: str = '', owner_email: str = DEFAULT_OWNER_EMAIL,
                owner_uid: str | None = None) -> int:
    """Add a new birth profile.

    Returns:
        The ID of the new profile
    """
    conn = get_connection()
    cursor = conn.execute('''
        INSERT INTO profiles (owner_email, owner_uid, name, birth_date, birth_time, birth_place, latitude, longitude, tz_offset, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (owner_email, owner_uid, name, birth_date, birth_time, birth_place, latitude, longitude, tz_offset, notes))
    conn.commit()
    profile_id = int(cursor.lastrowid or 0)
    conn.close()
    return profile_id


def get_profile(profile_id: int, owner_email: str = DEFAULT_OWNER_EMAIL) -> dict | None:
    """Get a profile by ID."""
    conn = get_connection()
    row = conn.execute('SELECT * FROM profiles WHERE id = ? AND owner_email = ?', (profile_id, owner_email)).fetchone()
    conn.close()
    return dict(row) if row else None


def list_profiles(owner_email: str = DEFAULT_OWNER_EMAIL) -> list[dict]:
    """List all profiles."""
    conn = get_connection()
    rows = conn.execute('SELECT * FROM profiles WHERE owner_email = ? ORDER BY name', (owner_email,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def update_profile(profile_id: int, owner_email: str = DEFAULT_OWNER_EMAIL, **kwargs) -> bool:
    """Update a profile's fields."""
    allowed = {'name', 'birth_date', 'birth_time', 'birth_place', 'latitude', 'longitude', 'tz_offset', 'notes'}
    fields = {k: v for k, v in kwargs.items() if k in allowed}
    if not fields:
        return False

    set_clause = ', '.join(f'{k} = ?' for k in fields)
    values = list(fields.values()) + [profile_id]

    conn = get_connection()
    values.append(owner_email)
    conn.execute(f'UPDATE profiles SET {set_clause}, updated_at = datetime("now") WHERE id = ? AND owner_email = ?', values)
    conn.commit()
    conn.close()
    return True


def delete_profile(profile_id: int, owner_email: str = DEFAULT_OWNER_EMAIL) -> bool:
    """Delete a profile."""
    conn = get_connection()
    cursor = conn.execute('DELETE FROM profiles WHERE id = ? AND owner_email = ?', (profile_id, owner_email))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted


def assign_owner_uid(owner_email: str, owner_uid: str) -> int:
    """Attach a Firebase UID to existing rows for one owner email."""
    conn = get_connection()
    cursor = conn.execute(
        'UPDATE profiles SET owner_uid = ? WHERE owner_email = ? AND (owner_uid IS NULL OR owner_uid = "")',
        (owner_uid, owner_email),
    )
    conn.commit()
    count = cursor.rowcount
    conn.close()
    return count


def load_user_ai_settings(owner_email: str) -> dict | None:
    conn = get_connection()
    row = conn.execute(
        'SELECT config_json FROM user_ai_settings WHERE owner_email = ?',
        (owner_email,),
    ).fetchone()
    conn.close()
    if not row:
        return None
    try:
        return json.loads(row['config_json'])
    except Exception:
        return None


def save_user_ai_settings(owner_email: str, config: dict):
    conn = get_connection()
    conn.execute(
        '''
        INSERT INTO user_ai_settings (owner_email, config_json, updated_at)
        VALUES (?, ?, datetime('now'))
        ON CONFLICT(owner_email) DO UPDATE SET
            config_json = excluded.config_json,
            updated_at = datetime('now')
        ''',
        (owner_email, json.dumps(config)),
    )
    conn.commit()
    conn.close()


def seed_default_profiles():
    """Seed the database with default profiles if empty."""
    profiles = list_profiles(DEFAULT_OWNER_EMAIL)
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
        add_profile(name, bdate, btime, place, lat, lon, owner_email=DEFAULT_OWNER_EMAIL)


# Initialize on import
init_db()
