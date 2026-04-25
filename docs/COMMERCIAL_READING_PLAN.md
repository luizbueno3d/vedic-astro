# Commercial Reading Plan

## 1. Product Goal

Turn Vedic Astro into a paid Vedic astrology reading platform where users can create an account, enter birth data, buy a reading, generate a beautiful structured Vedic astrology life map, and download it as a PDF.

Initial languages are English and Brazilian Portuguese. Future languages should remain possible through a scalable locale and translation-key foundation, not a hardcoded two-language shortcut.

## 2. Current Strengths

- Existing FastAPI + Jinja application with a focused server-rendered architecture.
- Railway deployment via `Procfile`.
- Firebase authentication as the production login path.
- Owner-scoped birth profiles.
- D1 dashboard with chart, dashas, transits, KP/Bhava Chalit, yogas, aspects, and exports.
- Dedicated dasha, vargas, analysis, compatibility, and reading surfaces.
- KP/Bhava Chalit support with verified sensitive mappings guarded by QA.
- D9/D10 and broader varga inspection with higher vargas marked cautiously.
- Jaimini indicators and Chara Dasha support.
- Synthesis and AI-assisted reading flow.
- Account-scoped AI provider settings.
- Current QA baseline: `python3 backend/tests/test_qa.py`.

## 3. Reading Philosophy

- D1 / Rashi chart is the base chart and primary interpretive foundation.
- KP / Bhava Chalit refines lived reality and should be compared with D1, not blindly replace it.
- D9, D10, Jaimini, and other layers refine interpretation rather than override D1.
- Higher vargas remain secondary until each formula and use case is individually verified.
- The reading should use real Vedic terms with short explanations in brackets, such as `Mahadasha (major planetary life period)` and `Atma Karaka (soul significator)`.
- Avoid generic AI-spiritual text, vague praise, and unsupported claims.
- The reading must feel specific, grounded in the actual chart, useful, and human.

## 4. First Sellable Product

Name:

- English: Life Map Reading
- Portuguese: Mapa de Vida Védico

Core sections:

- Birth data confirmation
- Method explanation
- D1 foundation
- Identity / life pattern
- KP / Bhava Chalit lived shifts
- Current Mahadasha / Antardasha
- Key placements
- Atma Karaka: soul significator, life direction, core karmic lesson
- Amatya Karaka: career/work significator, vocation, execution, money-making pathway
- Strengths and tensions
- Practical guidance
- Conclusion / life map summary

The first product should be a polished life-map report, not a raw chart dump. Rule-based calculations should provide the factual skeleton; AI should provide the human narrative only after receiving a structured, audited chart context.

## 5. Commercial Architecture

Planned flow:

`landing page -> locale selection -> signup/login -> birth profile -> choose reading product -> checkout -> confirmed payment -> generation -> stored reading -> PDF download`

Key rules:

- Payment creates entitlement; generation consumes that entitlement.
- Generated readings are stored and versioned.
- PDF exports are rendered from stored reading content, not from live recalculation.
- The reading language is chosen before generation and stored with the order.

## 6. Required Data Concepts

Minimal concepts/tables:

- `users`: Firebase UID, email, display name, default locale, timestamps.
- `birth_profiles`: existing profiles plus owner/user link, timezone metadata, and birth-data confidence.
- `reading_products`: product code, active flag, localized title/description keys, price, currency, template version.
- `reading_orders`: user, profile, product, locale, campaign tier, price, currency, payment identifiers, and state.
- `generated_readings`: order, profile snapshot, calculation snapshot, generated content, provider/model, status, and template version.
- `reading_exports`: reading, export format, generated file reference, checksum, timestamp.
- `locale/language preference`: user default plus per-order reading language.
- `calculation snapshots`: immutable chart facts used for the paid reading.
- `Jaimini indicators`: Atma Karaka and Amatya Karaka planet, sign, nakshatra, pada, D1 house, KP/Bhava Chalit house where applicable, and interpretive role.

Keep this compatible with SQLite for early staged launch. Before serious paid scale, migrate or harden persistence with managed Postgres, backups, and durable file storage.

Initial implementation note:

- `users`, `reading_products`, `reading_orders`, `generated_readings`, and `reading_exports` now exist as additive SQLite tables.
- The existing `profiles` table remains the active birth-profile table.
- `reading_orders.owner_email` is retained for account isolation while the future `users` table is introduced gradually.
- `reading_products` seeds `life_map` without overwriting existing production rows.
- Order creation and generation gating are wired without Stripe checkout yet.

Snapshot implementation note:

- `backend/engine/commercial_reading.py` now builds a deterministic `life_map_v1` snapshot.
- The snapshot includes profile facts, D1, KP/Bhava Chalit shifts, current Vimshottari timing, D9/D10, Jaimini Atma Karaka and Amatya Karaka indicators, localized section JSON, and Markdown.
- `/commercial-reading/snapshot/{profile_id}` exposes an authenticated inspection endpoint.
- The snapshot does not call AI.

Order-gate implementation note:

- `POST /reading-orders` creates an owner-scoped `pending_payment` order using server-side product pricing.
- `POST /reading-orders/{order_id}/generate` refuses generation unless the order status is `paid`.
- Successful generation stores immutable paid-reading content in `generated_readings`.
- `POST /reading-orders/{order_id}/checkout` creates a hosted Stripe Checkout Session from the server-side order price.
- `POST /stripe/webhook` verifies Stripe signatures and idempotently marks paid orders.
- Campaign pricing is recalculated before Checkout Session creation so checkout sessions, not abandoned pending orders, reserve launch-campaign slots.

## 7. i18n Direction

- Start with `en` and `pt-BR`.
- UI locale and reading language must be explicit; they may default together, but should not be treated as the same permanent value.
- Paid generated reading content should be stored in the chosen language.
- Do not dynamically translate paid generated content after generation.
- Use stable translation keys and locale files, for example `locales/en.json` and `locales/pt-BR.json`.
- Pass reading language explicitly into AI prompts, e.g. `Output language: Brazilian Portuguese`.
- Keep calculation identifiers language-neutral internally; translate labels at the presentation layer.

## 8. Payment Direction

Stripe is the payment provider foundation. Checkout Session creation and verified webhook confirmation are now wired at the backend level.

Current state machine:

`pending_payment -> paid -> generating -> complete / failed`

Rules:

- Only paid orders can generate readings.
- Stripe webhook verification is required before marking an order as paid.
- Webhook handling must be idempotent.
- Pricing must be server-side only.
- Campaign pricing:
  - First 100 paid readings: R$ 10,99
  - Next 100 paid readings: R$ 59,99
  - Normal price: R$ 99,99

Campaign counters should be based on confirmed paid orders, not client-side claims or checkout-page values.

## 9. Production Risks

- SQLite persistence and backups on Railway need hardening before serious paid scale.
- AI API keys stored plainly in SQLite JSON should be reconsidered before opening the product broadly.
- Local-only AI providers should not appear in production-facing flows.
- Hardcoded English must be replaced gradually with translation keys.
- Higher vargas should not be overmarketed until verified.
- Paid readings need immutable snapshots so later engine changes do not silently alter already purchased reports.
- Auth/profile ownership changes must preserve strict user-data separation.

## 10. Implementation Phases

1. Roadmap document
2. i18n foundation
3. Reading product/order schema
4. Deterministic commercial reading snapshot generator
5. Paid order gate
6. Stripe checkout/webhook
7. PDF export from stored reading
8. Admin order view

Each phase should preserve the existing QA baseline and avoid broad rewrites of the astrology engine.

Current implementation status:

- Phases 1-6 have backend foundations in place.
- The dashboard now has a minimal user-facing buy/checkout/status/generate surface for the first product.
- Phase 7 is the next commercial backend step and should export PDF from stored generated readings.

## 11. Immediate Next Step

Next recommended coding task: implement PDF export from stored generated readings.

Scope:

- Render the stored `generated_readings.content_markdown` / section JSON, not live recalculation.
- Create a durable `reading_exports` record.
- Keep the PDF language identical to the paid generated reading language.
- Avoid local-only tooling that will not work on Railway.
- Run `python3 backend/tests/test_qa.py` after changes.

## 12. Strategic Additions

- Add birth-data confidence and timezone confirmation before paid checkout.
- Version every reading template, prompt, and calculation snapshot.
- Create internal audit views for generated readings before scaling sales.
- Keep a product ladder open: Life Map, Career/Vocation, Relationship, Current Dasha Year, and Compatibility.
- Consider a premium human-review option later, but keep the first launch automated and tightly scoped.
- Use sample anonymized readings for marketing; never expose real user chart data.
