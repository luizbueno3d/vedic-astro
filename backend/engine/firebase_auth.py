"""Firebase auth helpers.

This module keeps Firebase optional. If env vars are not configured, the app keeps
working with the current password gate while remaining ready for Google and
email/password Firebase sign-in later.
"""

from __future__ import annotations

import os

try:
    import firebase_admin
    from firebase_admin import auth, credentials
except Exception:  # pragma: no cover - optional until deployed with dependency
    firebase_admin = None
    auth = None
    credentials = None


_APP = None


def get_firebase_web_config() -> dict:
    return {
        'apiKey': os.getenv('FIREBASE_API_KEY', ''),
        'authDomain': os.getenv('FIREBASE_AUTH_DOMAIN', ''),
        'projectId': os.getenv('FIREBASE_PROJECT_ID', ''),
        'storageBucket': os.getenv('FIREBASE_STORAGE_BUCKET', ''),
        'messagingSenderId': os.getenv('FIREBASE_MESSAGING_SENDER_ID', ''),
        'appId': os.getenv('FIREBASE_APP_ID', ''),
    }


def firebase_client_enabled() -> bool:
    config = get_firebase_web_config()
    return bool(config['apiKey'] and config['authDomain'] and config['projectId'] and config['appId'])


def firebase_admin_enabled() -> bool:
    return all([
        firebase_admin is not None,
        os.getenv('FIREBASE_PROJECT_ID'),
        os.getenv('FIREBASE_CLIENT_EMAIL'),
        os.getenv('FIREBASE_PRIVATE_KEY'),
    ])


def _get_app():
    global _APP
    if _APP is not None:
        return _APP
    if not firebase_admin_enabled():
        return None
    if firebase_admin._apps:
        _APP = firebase_admin.get_app()
        return _APP

    private_key = os.getenv('FIREBASE_PRIVATE_KEY', '').replace('\\n', '\n')
    cred = credentials.Certificate({
        'type': 'service_account',
        'project_id': os.getenv('FIREBASE_PROJECT_ID'),
        'private_key_id': os.getenv('FIREBASE_PRIVATE_KEY_ID', ''),
        'private_key': private_key,
        'client_email': os.getenv('FIREBASE_CLIENT_EMAIL'),
        'client_id': os.getenv('FIREBASE_CLIENT_ID', ''),
        'token_uri': 'https://oauth2.googleapis.com/token',
    })
    _APP = firebase_admin.initialize_app(cred)
    return _APP


def verify_firebase_id_token(id_token: str) -> dict | None:
    app = _get_app()
    if not app or not auth:
        return None
    try:
        return auth.verify_id_token(id_token, app=app)
    except Exception:
        return None
