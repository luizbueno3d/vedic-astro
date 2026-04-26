# Vedic Astro / LogicCosmo

This repository is the keeper for the full LogicCosmo platform:

- GitHub: `https://github.com/luizbueno3d/vedic-astro`
- Local repo: `/Users/luizbueno/vedic-astro`
- Public brand/domain: `logicosmo.com`
- Expert/private domain target: `expert.logicosmo.com`

The original Vedic Astro app remains the expert/internal astrology cockpit. LogicCosmo is the commercial customer-facing product built on top of the same calculation engine, auth, profile, payment, and reading-generation foundations.

It is currently a server-rendered FastAPI + Jinja application with an in-house astrology engine for D1, dashas, KP/BCC, divisional charts, transits, compatibility, synthesized readings, paid reading orders, and account-scoped AI assistance.

## Product Architecture Direction

The platform should use one GitHub repo and one FastAPI codebase for the near term, with clean separation between public customer routes and expert/private routes.

### Public Product: `logicosmo.com`

LogicCosmo is the commercial storefront and paid reading delivery experience.

Public users should be able to:

- Understand the reading product in simple beginner-safe language
- Create an account or log in
- Enter and confirm birth data
- Choose the Life Map Reading / Mapa de Vida Védico
- Pay through Stripe Checkout
- Generate/view a stored reading only after confirmed payment
- Download a PDF once export support is implemented

The public app should hide expert dashboards, raw calculation tools, AI settings, KP/BCC internals, varga inspection, and dense astrology tables unless they are translated into useful reading content.

### Expert Product: `expert.logicosmo.com`

The existing app becomes the expert cockpit.

Expert users should retain access to:

- Dashboard
- Dasha
- Analysis
- Vargas
- KP/Bhava Chalit and BCC inspection
- Compatibility
- AI Interpretations and AI Settings
- Exports
- Calculation verification and fulfillment tools

This expert app is not being removed. It is the laboratory, verification cockpit, and future admin/fulfillment workspace. Normal customers must not see it unless explicitly granted expert/admin access.

### Why Keep One Repo First

One repo is the right near-term choice because the existing app already contains the hard parts:

- Authentication
- Owner-scoped birth profiles
- SQLite data layer
- Stripe order/webhook foundation
- Paid-generation gate
- Stored commercial reading snapshots
- QA coverage for core calculations and payment state

A separate frontend repo can be considered later, but splitting now would add API auth, CORS, deployment, session, and integration complexity before the public product has proven itself.

Current working model:

- Keep `/Users/luizbueno/logicosmo` as the standalone design prototype/source
- Port the approved public UX into FastAPI/Jinja public templates
- Keep expert/internal screens inside this repo
- Deploy `logicosmo.com` to the public routes
- Deploy or route `expert.logicosmo.com` to expert-only routes

## Route Separation Plan

Planned public/customer routes:

- `/`
- `/pt-BR`
- `/en`
- `/readings/life-map`
- `/birth-profile`
- `/checkout`
- `/orders/{order_id}`
- `/orders/{order_id}/reading`
- `/orders/{order_id}/export.pdf`

Planned expert/private routes:

- `/expert`
- `/expert/dashboard`
- `/expert/dasha`
- `/expert/analysis`
- `/expert/vargas`
- `/expert/compatibility`
- `/expert/ai`
- `/expert/settings`
- `/expert/orders`

Existing expert routes may remain temporarily for compatibility, but they should become protected and eventually redirect into the `/expert/*` namespace.

## Access Model Direction

The app needs explicit role/access levels:

- `customer` - can manage own profile, orders, readings, and downloads
- `expert` - can access the private astrology cockpit
- `admin` - can review orders, users, and fulfillment state
- `master_admin` - full platform owner access

Luiz’s account should become `master_admin`.

Important invariants:

- Customers can only access their own profiles, orders, generated readings, and exports
- Customers cannot access expert dashboards by guessing URLs
- Expert/admin features must never rely on hidden navigation alone
- Paid reading generation must remain server-gated by confirmed payment state

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

The current surfaces are expert/internal surfaces unless explicitly adapted into the public LogicCosmo product.

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
- Normal customer accounts should not see expert/private routes
- Expert/private routes should be protected by role, not just hidden from navigation

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
The LogicCosmo public/expert platform direction is documented in `LOGICOSMO.md`.

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

The dashboard includes the first minimal user-facing purchase surface for `life_map`: it shows the current server-side campaign price, creates an order, redirects to Stripe Checkout, displays return status, and exposes reading generation only after the order is `paid`.

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

## LogicCosmo Public UX Prototype

A standalone static prototype currently exists outside this repo at:

- `/Users/luizbueno/logicosmo`

That prototype uses the Claude-generated design system from:

- `LogicCosmo Design System/`

The prototype is a visual/product scaffold only. It does not save real profiles, call Stripe, call the astrology engine, or generate real readings.

Its role is to define the public customer experience before porting the approved screens into FastAPI/Jinja templates.

The next implementation target is to fold the prototype into this repo as:

- `templates/public/*` for marketing/customer pages
- `static/public/*` for public assets/styles/scripts
- `templates/expert/*` or equivalent organization for expert/private pages over time

## Migration Plan

The safe migration sequence is:

1. Preserve the existing expert app and QA baseline.
2. Add public LogicCosmo routes/templates without removing expert routes.
3. Add role/access checks for expert/private surfaces.
4. Move public checkout/order UX out of the expert dashboard and into public customer pages.
5. Make `logicosmo.com` the public customer entrypoint.
6. Make `expert.logicosmo.com` the private expert/admin entrypoint.
7. Add stored-reading PDF export from generated reading content.
8. Add admin order review/fulfillment tools.
9. Gradually adapt selected expert insights into simplified customer-facing reading sections.

Do not move expert functionality into the public product directly. Translate it into structured reading content only when it is verified, useful, and beginner-safe.

## Deployment

- Hosted on Railway
- Procfile command: `uvicorn backend.api.main:app --host 0.0.0.0 --port $PORT`
- Firebase env vars must be configured in Railway, not only in local `.env`
- `logicosmo.com` should eventually point to the public/customer routes
- `expert.logicosmo.com` should eventually point to expert/private routes
- Stripe redirect URLs and webhook URLs must be updated when the production domain switches from the Railway URL to `logicosmo.com`

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
- `LOGICOSMO.md`: public LogicCosmo + expert/private architecture plan
- `docs/OPERATIONS.md`: auth, deployment, AI, exports, and maintenance notes
- `docs/COMMERCIAL_READING_PLAN.md`: commercial roadmap for paid readings, i18n, payments, PDF, and admin flow

## Repo Hygiene

- Do not casually commit secrets
- `backend/data/ai_config.json` should stay out of git for normal use
- `backend/data/profiles.db` is user data, not code
