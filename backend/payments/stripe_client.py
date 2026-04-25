"""Minimal Stripe Checkout integration.

Uses Stripe's HTTP API directly so local QA does not require an extra package.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import time
from urllib.parse import urljoin

import requests


STRIPE_API_BASE = os.getenv("STRIPE_API_BASE", "https://api.stripe.com")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")


class StripeConfigError(RuntimeError):
    """Stripe is not configured for the requested operation."""


class StripeAPIError(RuntimeError):
    """Stripe API returned an unsuccessful response."""

    def __init__(self, message: str, status_code: int | None = None, details: dict | None = None):
        super().__init__(message)
        self.status_code = status_code
        self.details = details or {}


class StripeSignatureError(ValueError):
    """Stripe webhook signature could not be verified."""


def stripe_configured() -> bool:
    return bool(STRIPE_SECRET_KEY)


def stripe_webhook_configured() -> bool:
    return bool(STRIPE_WEBHOOK_SECRET)


def _stripe_locale(locale: str | None) -> str:
    if locale == "pt-BR":
        return "pt-BR"
    if locale == "en":
        return "en"
    return "auto"


def _stripe_post(path: str, data: dict, idempotency_key: str | None = None) -> dict:
    if not STRIPE_SECRET_KEY:
        raise StripeConfigError("STRIPE_SECRET_KEY is not configured")

    headers = {}
    if idempotency_key:
        headers["Idempotency-Key"] = idempotency_key

    response = requests.post(
        urljoin(STRIPE_API_BASE, path),
        data=data,
        auth=(STRIPE_SECRET_KEY, ""),
        headers=headers,
        timeout=15,
    )

    try:
        payload = response.json()
    except Exception:
        payload = {}

    if response.status_code >= 400:
        error = payload.get("error", {}) if isinstance(payload, dict) else {}
        message = error.get("message") or f"Stripe API error {response.status_code}"
        raise StripeAPIError(message, status_code=response.status_code, details=payload)

    return payload


def create_checkout_session(order: dict, product_name: str, success_url: str,
                            cancel_url: str, customer_email: str | None = None) -> dict:
    """Create a hosted Stripe Checkout Session for a one-time reading purchase."""
    order_id = str(order["id"])
    owner_email = order["owner_email"]
    metadata = {
        "reading_order_id": order_id,
        "owner_email": owner_email,
        "profile_id": str(order["profile_id"]),
        "product_code": order["product_code"],
        "locale": order["locale"],
    }
    data = {
        "mode": "payment",
        "success_url": success_url,
        "cancel_url": cancel_url,
        "client_reference_id": order_id,
        "customer_email": customer_email or owner_email,
        "locale": _stripe_locale(order.get("locale")),
        "line_items[0][quantity]": "1",
        "line_items[0][price_data][currency]": str(order["currency"]).lower(),
        "line_items[0][price_data][unit_amount]": str(int(order["price_cents"])),
        "line_items[0][price_data][product_data][name]": product_name,
        "submit_type": "pay",
    }

    for key, value in metadata.items():
        data[f"metadata[{key}]"] = value
        data[f"payment_intent_data[metadata][{key}]"] = value

    return _stripe_post(
        "/v1/checkout/sessions",
        data,
        idempotency_key=f"reading-order-{order_id}-checkout",
    )


def _parse_signature_header(signature_header: str) -> tuple[int, list[str]]:
    timestamp = None
    signatures = []
    for item in signature_header.split(","):
        key, _, value = item.partition("=")
        if key == "t":
            try:
                timestamp = int(value)
            except ValueError as exc:
                raise StripeSignatureError("Invalid Stripe signature timestamp") from exc
        elif key == "v1" and value:
            signatures.append(value)

    if timestamp is None or not signatures:
        raise StripeSignatureError("Missing Stripe signature values")
    return timestamp, signatures


def verify_webhook_signature(payload: bytes, signature_header: str, endpoint_secret: str,
                             tolerance_seconds: int = 300, now: int | None = None) -> bool:
    """Verify Stripe webhook payload with the v1 HMAC signature."""
    if not endpoint_secret:
        raise StripeConfigError("STRIPE_WEBHOOK_SECRET is not configured")
    timestamp, signatures = _parse_signature_header(signature_header or "")
    current_time = int(now if now is not None else time.time())
    if tolerance_seconds and abs(current_time - timestamp) > tolerance_seconds:
        raise StripeSignatureError("Stripe webhook timestamp is outside tolerance")

    signed_payload = f"{timestamp}.{payload.decode('utf-8')}".encode("utf-8")
    expected = hmac.new(
        endpoint_secret.encode("utf-8"),
        signed_payload,
        hashlib.sha256,
    ).hexdigest()
    if not any(hmac.compare_digest(expected, signature) for signature in signatures):
        raise StripeSignatureError("Stripe webhook signature mismatch")
    return True


def construct_webhook_event(payload: bytes, signature_header: str,
                            endpoint_secret: str | None = None) -> dict:
    """Verify and parse a Stripe webhook event."""
    secret = endpoint_secret if endpoint_secret is not None else STRIPE_WEBHOOK_SECRET
    verify_webhook_signature(payload, signature_header, secret)
    try:
        return json.loads(payload.decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise StripeSignatureError("Invalid Stripe webhook JSON payload") from exc
