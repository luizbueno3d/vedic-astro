# Vedic Astro

Private Vedic astrology web app built at `/Users/bueno/vedic-astro`.

It is a server-rendered FastAPI + Jinja application with an in-house astrology engine for D1, dashas, KP/BCC, divisional charts, transits, compatibility, synthesized readings, and account-scoped AI assistance.

## What The App Does

- Authenticated profile-based astrology workspace
- D1 dashboard with current dasha, transit reading, D9 quick view, KP/BCC, yogas, conjunctions, aspects, and exports
- Dedicated dasha page with Vimshottari and Jaimini timing
- Analysis page for yogas, doshas, Jaimini, Bhavat Bhavam, strengths, and structural logic
- Vargas page for D9, D10, and broader divisional chart inspection
- Compatibility page with Guna Milan and broader synastry context
- Reading page with rule-based synthesis plus AI interpretation
- AI settings with account-scoped provider/model/API-key persistence

## Stack

- Backend: FastAPI
- Templates: Jinja2
- Runtime: Python 3.11
- Data store: SQLite in `backend/data/profiles.db`
- Core astrology logic: `backend/engine/*.py`
- Deploy target: Railway via `Procfile`

## Key Paths

- App entry: `backend/api/main.py`
- Data layer: `backend/data/database.py`
- Templates: `templates/`
- Locales: `locales/`
- Static assets: `static/`
- Core engines:
  - `backend/engine/ephemeris.py`
  - `backend/engine/charts.py`
  - `backend/engine/dasha.py`
  - `backend/engine/kp.py`
  - `backend/engine/transits.py`
  - `backend/engine/synthesis.py`
  - `backend/engine/llm_reading.py`
  - `backend/engine/ai_provider.py`

## Main Product Surfaces

### Dashboard

- D1 North Indian chart
- Planetary positions
- Current Mahadasha / Antardasha summary
- Simplified dashboard export
- Separate full dasha export
- Transit table + transit reading
- D9 quick view
- KP / Bhava Chalit visualization
- House rulerships, yogas, conjunctions, aspects
- Floating AI chat dock

### Dasha

- Vimshottari timeline
- Current dasha reading
- Chara Dasha support
- Timing-oriented AI follow-up questions via dock

### Analysis

- Yogas
- Doshas
- Jaimini
- Bhavat Bhavam
- Strength-oriented structural reading

### Vargas

- Core and advanced divisional charts
- D9 and D10 are especially important in current UX

### Compatibility

- Guna Milan
- Synastry context

### Reading / AI

- Rule-based synthesis
- Long-form AI reading
- Small page-level AI chat dock on core surfaces

## Auth And Ownership Model

- Firebase login is the intended auth path
- Shared password login was removed from the main flow
- Session cookie + session owner identity gate access
- Profiles are scoped by authenticated owner email
- AI provider config is also scoped by authenticated owner email
- Commercial reading records are designed to preserve `owner_email` for ownership checks even as a future `users` table is introduced.

Important invariant:

- The logged-in user should only see their own profiles and saved AI settings

## AI Provider System

Current provider support includes:

- OpenAI
- Anthropic
- Groq
- OpenRouter
- MiniMax
- Kilo Gateway
- Z.AI
- Ollama

Behavior notes:

- Settings are saved per user in SQLite, not just local file config
- OpenRouter free models use retry + fallback handling for `429`
- MiniMax uses provider-specific integration logic, not naive OpenAI compatibility
- Z.AI is supported directly through its own API key and OpenAI-compatible base URL

## Commercial Reading Foundation

The commercial product direction is documented in `docs/COMMERCIAL_READING_PLAN.md`.

Current database foundation includes additive SQLite tables for:

- `users` - future Firebase-backed account records
- `reading_products` - sellable reading definitions
- `reading_orders` - payment and generation state for purchased readings
- `generated_readings` - stored reading content and immutable calculation snapshots
- `reading_exports` - PDF/markdown/text/json export records

The deterministic Life Map snapshot generator lives in `backend/engine/commercial_reading.py`.
It produces a stored-ready structure with:

- profile snapshot
- D1 calculation snapshot
- KP/Bhava Chalit house shifts
- current dasha snapshot
- D9/D10 confirmation data
- Jaimini Atma Karaka and Amatya Karaka indicators
- localized section JSON and Markdown

Inspection endpoint:

- `/commercial-reading/snapshot/{profile_id}`

This endpoint is authenticated and does not call AI, check payment, store orders, or generate PDF files yet.

Order-gate endpoints:

- `GET /reading-products` - list active products with localized labels
- `POST /reading-orders` - create a server-priced `pending_payment` order
- `POST /reading-orders/{order_id}/checkout` - create or reuse a Stripe Checkout Session
- `GET /reading-orders` - list owner-scoped orders
- `GET /reading-orders/{order_id}` - show one owner-scoped order and stored reading if present
- `POST /reading-orders/{order_id}/generate` - generate only when order status is `paid`
- `POST /stripe/webhook` - public Stripe webhook endpoint with signature verification

The order gate is deliberately conservative. It creates pending orders and blocks generation with `payment_required` until a verified Stripe webhook marks the order as paid.

The first seeded product is:

- Code: `life_map`
- English: Life Map Reading
- Portuguese: Mapa de Vida Védico
- Standard price: `BRL 99.99`
- Template version: `life_map_v1`

Required payment env vars:

- `STRIPE_SECRET_KEY`
- `STRIPE_WEBHOOK_SECRET`
- `APP_BASE_URL` or `PUBLIC_BASE_URL` for production redirect URLs

Paid readings move through:

`pending_payment -> paid -> generating -> complete / failed`

Only confirmed paid orders should be allowed to generate customer readings.

## Deployment

- Hosted on Railway
- Procfile command: `uvicorn backend.api.main:app --host 0.0.0.0 --port $PORT`
- Firebase env vars must be configured in Railway, not only in local `.env`

## Local Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn backend.api.main:app --reload
```

## Verification

Main regression command:

```bash
python3 backend/tests/test_qa.py
```

This currently passes 101/101 checks when the app is healthy.

## Current Documentation Set

- This file: project overview
- `docs/OPERATIONS.md`: auth, deployment, AI, exports, and maintenance notes
- `docs/COMMERCIAL_READING_PLAN.md`: commercial roadmap for paid readings, i18n, payments, PDF, and admin flow

## Repo Hygiene

- Do not casually commit secrets
- `backend/data/ai_config.json` should stay out of git for normal use
- `backend/data/profiles.db` is user data, not code
