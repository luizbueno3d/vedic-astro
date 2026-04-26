# LogicCosmo Public Product Architecture

## Executive Direction

LogicCosmo is the public customer-facing product. The existing `vedic-astro` application remains the expert/internal engine room.

The current app has proven the commercial backend path works:

`login -> profile -> order -> Stripe test payment -> verified webhook -> paid status -> stored reading generation`

That does not mean the current expert dashboard should become the public product. The existing dashboard is dense by design: D1, KP/Bhava Chalit, dashas, vargas, Jaimini, compatibility, exports, and AI settings are useful for internal verification and expert work, but they are not beginner-proof. LogicCosmo should sell and deliver a polished reading, not expose a technical astrology cockpit.

## Current Decision Snapshot

- Recommended architecture: same FastAPI app for now, with separate public/customer routes and templates, plus explicit role gates for expert/admin routes.
- Expert app role: keep `vedic-astro` as the internal calculation cockpit and verification workspace.
- Public app role: build `LogicCosmo.com` as the simple storefront, customer account, checkout, reading view, and PDF delivery experience.
- First safe implementation task: add `templates/public/base_public.html`, `templates/public/landing.html`, and public routes for `/`, `/pt-BR`, and `/en`.
- Important constraint: do not move, remove, or simplify existing expert routes while introducing the public surface.
- QA baseline after this documentation pass: `python3 backend/tests/test_qa.py` passes `101/101`.

## Product Split

### Keep `vedic-astro` As Expert/Internal

Primary purposes:

- Calculation verification cockpit.
- Internal astrology workspace.
- Admin/fulfillment/review surface.
- Advanced KP/Bhava Chalit, Dasha, Vargas, Jaimini, Compatibility, AI settings, and exports.
- Regression and trust-map development for the astrology engine.

Rules:

- Do not remove expert routes.
- Do not simplify expert dashboards for public users.
- Do not break existing private workflows.
- Do not rewrite the astrology engine.
- Preserve `python3 backend/tests/test_qa.py` as the baseline gate.

### Create LogicCosmo As Public Product

Primary purposes:

- Public storefront.
- Beginner-friendly Vedic astrology education.
- Account and birth-data onboarding.
- Reading purchase flow.
- Stored reading view.
- PDF download once export exists.
- Future product ladder for other reading types.

The public product should hide raw astrology tooling unless a specific concept is useful and explained in plain language.

## Architecture Options

### Option A: Same FastAPI App, Separate Public Routes/Templates

Structure:

- Same Railway service.
- Same codebase and engine imports.
- Separate public route namespace and templates.
- Role-based gates hide expert surfaces from normal customers.

Pros:

- Fastest and safest path from current code.
- Reuses existing auth, profile, order, Stripe, i18n, and reading snapshot logic.
- No network boundary between storefront and engine.
- No API contract overhead yet.
- Lower operational complexity while product is still forming.

Cons:

- Strong route/template discipline is required to avoid leaking expert UI.
- Customer and expert concerns live in one process.
- Long-term brand/app separation may eventually benefit from a separate deploy.

### Option B: Separate FastAPI App In Same Repo

Structure:

- Same repository and engine package.
- Two app entrypoints, for example `backend/api/main.py` and `backend/public/main.py`.
- Railway could run one or two services from the same repo.

Pros:

- Cleaner runtime separation.
- Public app can have different middleware, nav, auth gates, and templates.
- Still reuses local engine code without publishing a separate package.

Cons:

- More deployment setup.
- Shared database/session behavior must be handled carefully.
- More code paths before product-market fit.

### Option C: Separate Repo Consuming Existing Engine/API

Structure:

- Public LogicCosmo app in a separate repo.
- Existing app exposes internal APIs or packaged engine functions.

Pros:

- Strongest separation.
- Clean public codebase and deployment lifecycle.
- Easier to scale teams and permissions later.

Cons:

- Premature operational complexity.
- Requires API hardening before the public product is stable.
- Introduces versioning and deployment coordination between repos.

### Recommendation

Start with **Option A: same FastAPI app, separate public routes/templates, plus explicit roles/access gates**.

Reasoning:

- The backend commerce path already works in this app.
- We need product clarity faster than infrastructure complexity.
- The engine should not be wrapped behind a premature API boundary until reading snapshots, PDF export, and public UX are stable.
- We can evolve to Option B later by moving public routes/templates into a separate app entrypoint without changing the engine.

Target medium-term path:

1. Start with separate public routes/templates in the same app.
2. Add roles and expert-only route protection.
3. Extract public route module and template namespace.
4. If needed, split into a second Railway service using the same repo.
5. Only later consider a separate repo or engine package.

## Route Structure

### Public Routes

Locale-aware marketing and onboarding:

- `GET /` -> public landing, locale auto-detected or defaults to `pt-BR` for Brazilian traffic when possible.
- `GET /pt-BR` -> Portuguese landing.
- `GET /en` -> English landing.
- `GET /readings/life-map` -> product page for Life Map Reading / Mapa de Vida Vedico.
- `GET /how-it-works` -> beginner-friendly explanation of Vedic astrology and the reading process.
- `GET /pricing` -> launch campaign and standard price explanation.

Customer account and order flow:

- `GET /account` -> customer home: birth profiles, orders, next steps.
- `GET /birth-profile` -> create/confirm birth data.
- `POST /birth-profile` -> save owner-scoped profile.
- `GET /checkout?profile_id=...&product=life_map` -> review selected profile, reading language, and current server-side price.
- `POST /checkout` -> create order and redirect/create Stripe Checkout Session.
- `GET /orders/{order_id}` -> owner-scoped order status.
- `GET /orders/{order_id}/reading` -> owner-scoped stored generated reading view.
- `POST /orders/{order_id}/generate` -> paid-only generation action, possibly triggered from the order page.
- `GET /orders/{order_id}/export.pdf` -> owner-scoped PDF download once implemented.

Public auth routes may reuse existing Firebase login mechanics, but the presentation should be customer-specific:

- `GET /login`
- `GET /signup`
- `POST /auth/firebase-login`
- `POST /logout`

### Expert/Internal Routes

Keep existing expert routes but mark them explicitly internal:

- `/dashboard`
- `/dasha`
- `/analysis`
- `/vargas`
- `/compatibility`
- `/reading`
- `/ai-settings`
- `/commercial-reading/snapshot/{profile_id}`
- raw calculation APIs such as `/chart/{profile_id}`, `/kp/{profile_id}`, `/jaimini/{profile_id}`, `/doshas/{profile_id}`

Recommended future namespace:

- `/expert/dashboard`
- `/expert/dasha`
- `/expert/analysis`
- `/expert/vargas`
- `/expert/compatibility`
- `/expert/ai-settings`

Migration rule:

- Keep old expert URLs during transition.
- Add redirects or aliases only after customer public routes exist.
- Do not expose expert links in public navigation.

## Template/UI Structure

Recommended layout:

```text
templates/
  public/
    base_public.html
    landing.html
    product_life_map.html
    how_it_works.html
    pricing.html
  customer/
    account.html
    birth_profile.html
    checkout.html
    order_status.html
    stored_reading.html
  expert/
    base_expert.html
    dashboard.html
    dasha.html
    analysis.html
    vargas.html
    compatibility.html
    reading.html
    ai_settings.html
  shared/
    locale_switcher.html
    auth_buttons.html
    flash.html
    price_badge.html
```

Initial implementation can keep current templates in place and add new public/customer templates. A later cleanup can move existing expert templates into `templates/expert/` once route tests are in place.

Public UI principles:

- Explain one thing at a time.
- Avoid raw chart dumps.
- Avoid expert navigation.
- Use short definitions for Vedic terms.
- Emphasize what the customer receives: a polished life map, not dashboard access.
- Support English and Brazilian Portuguese from the beginning.

Expert UI principles:

- Keep dense tools available.
- Make expert/internal status visually clear.
- Add admin/review functions here later.

## Public Design Direction

Current production direction: **DS2.1 editorial storefront**.

The first public visual pass was too close to a cosmic/SaaS dashboard. The second design exploration moved toward a stronger editorial language, but the raw prototype was too oversized and partly inconsistent across screens. The production direction should use DS2 as reference, not as a wholesale copy.

DS2.1 rules:

- Use a premium paper/document feeling rather than a glowing astrology-dashboard feeling.
- Keep the hero commercially clear above the fold: product, price, secure checkout, PDF, and CTA.
- Use strong ink typography, warm paper backgrounds, and copper/gold as a restrained accent.
- Make the reading preview look like a polished document/report, not a technical chart surface.
- Keep cosmic/orbital motifs subtle and decorative only.
- Avoid emoji in production UI.
- Avoid overlarge typography that breaks the viewport or hides the CTA.
- Keep English and Brazilian Portuguese copy switchable on public pages.
- Preserve the expert app visual language separately; do not force the public brand onto the internal cockpit yet.

Current public implementation files:

- `templates/public/base_public.html`
- `templates/public/landing.html`
- `templates/public/life_map.html`
- `static/public/styles/site.css`
- `static/public/scripts/app.js`

Design reference source:

- `LogicCosmo Design System 2/`

Do not commit personal/browser screenshots from design-tool upload folders unless explicitly needed for review history.

## Auth And Permissions

Current auth already supports Firebase login and owner-scoped profiles/orders. The public product needs an explicit role model.

Recommended user roles:

- `customer`: default account role. Can access public/customer routes and own data only.
- `expert`: can access expert/internal astrology workspace.
- `admin`: can manage orders, inspect generated readings, and later review fulfillment.

Data additions:

- Add `users.role` or `users.access_level`, default `customer`.
- Add helper functions:
  - `require_customer(request)`
  - `require_expert(request)`
  - `require_admin(request)`
- Keep all customer resources owner-scoped by `owner_email` / `user_id`.

Rules:

- Customers must not access expert dashboards by default.
- Expert/internal users may access public customer routes for testing.
- Admin tools must not trust client-supplied user/order/profile IDs without server-side ownership or role checks.

## Data Model

The current schema is mostly sufficient for the next phase:

- `users`
- `profiles`
- `reading_products`
- `reading_orders`
- `generated_readings`
- `reading_exports`

Recommended additions before public launch:

- `users.role` or `users.access_level` with default `customer`.
- `users.default_locale` / confirm existing `locale` behavior.
- `profiles.birth_data_confidence` or fields for timezone/source confirmation.
- `reading_orders.source` or `channel`, for example `public`, `expert_test`, `admin`.
- `reading_orders.reading_language` if we want clearer naming than `locale`.
- `generated_readings.viewed_at` optional.
- `reading_exports.storage_backend`, `file_key`, and `checksum` if moving beyond local SQLite/file paths.

Production hardening:

- SQLite is acceptable for test/sandbox and very early private beta.
- Before real customer volume, use managed Postgres or another durable database with backups.
- PDF exports should use durable storage or be regenerated from stored content in a deterministic way.

## Payment Flow

Keep the Stripe backend but move the customer-facing payment entry from the expert dashboard to the LogicCosmo public/customer flow.

Public flow:

1. Customer selects reading product.
2. Customer logs in or creates account.
3. Customer enters/chooses birth profile.
4. Server displays current server-side price.
5. Server creates `pending_payment` order.
6. Server creates Stripe Checkout Session.
7. Stripe webhook verifies payment and marks order `paid`.
8. Customer order page shows `paid` and allows generation.
9. Generated reading is stored.
10. Customer views/downloads stored reading.

Important rules:

- Price never comes from the browser.
- A pending order without a Stripe Checkout Session should not reserve campaign inventory.
- Duplicate webhook events must be idempotent.
- Expired checkout must not cancel an already-paid order.
- Expert/internal test buttons should be hidden or removed once public flow exists.

## Reading Generation

The public product must generate from a deterministic, stored snapshot.

Current working foundation:

- `backend/engine/commercial_reading.py` creates `life_map_v1` snapshots.
- `generated_readings` stores profile snapshot, calculation snapshot, Jaimini snapshot, section JSON, and Markdown.
- Generation is blocked unless order status is `paid`.

Public read/PDF rules:

- Reading view renders `generated_readings.content_json` / `content_markdown`.
- PDF renders stored content, not live calculations.
- If the astrology engine changes later, already-purchased readings must not silently change.
- Re-generation should be a controlled admin action, not an accidental page refresh.

Interpretation rules:

- D1/Rashi is the base chart.
- KP/Bhava Chalit refines lived reality and is compared with D1.
- D9/D10/Jaimini refine interpretation.
- Higher vargas remain secondary until verified.
- Include Atma Karaka as soul significator, life direction, and core karmic lesson.
- Include Amatya Karaka as career/work significator, vocation, execution, and money-making pathway.
- Use Vedic terms with explanations in brackets.
- Avoid generic AI-spiritual filler.
- Make content specific, grounded, useful, and beginner-readable.

## i18n

Initial locales:

- `en`
- `pt-BR`

Rules:

- UI locale and reading language must be explicit.
- Public landing can auto-detect locale from URL, session, or browser language.
- URL should allow explicit locale paths: `/pt-BR`, `/en`.
- Paid generated content must be stored in the chosen reading language.
- Do not dynamically translate paid generated readings after generation.
- Keep calculation identifiers language-neutral internally.
- Translate labels, headings, buttons, and explanations through stable keys.

Brazil-specific UX:

- Assume many users know Western astrology or only sun-sign astrology.
- Explain Vedic astrology as a different system without sounding superior or obscure.
- Use examples and plain human language.
- Avoid untranslated Sanskrit terms unless immediately explained.

## Domain And Deployment

Current state:

- Railway app: `https://web-production-db3d.up.railway.app`
- Commercial domain acquired: `logicosmo.com`
- Contact email: `info@logicosmo.com`

Recommended deployment path:

### Stage 1: Single Railway Service

- Same app serves public LogicCosmo routes and protected expert routes.
- `logicosmo.com` points to public landing.
- Expert app remains accessible at `/expert/...` or temporarily existing expert URLs.
- Add strict role gates before routing normal customers into expert pages.

### Stage 2: Split Railway Services If Needed

- One service for public LogicCosmo.
- One service for expert/internal Vedic Astro.
- Same repo or same engine package.
- Shared managed database with role-based access and careful migrations.

Domain considerations:

- Set Railway custom domain for `logicosmo.com` when DNS is ready.
- Update `APP_BASE_URL=https://logicosmo.com` only after the domain is attached and HTTPS works.
- Update Stripe webhook endpoint from Railway domain to `https://logicosmo.com/stripe/webhook` only after deploy is verified.
- Add `logicosmo.com` to Firebase authorized domains.
- Configure customer email sender/reply-to with `info@logicosmo.com` later.

Do not break the existing Railway flow while DNS is being configured.

## Migration Strategy

### Phase 1: Architecture Documentation

Goal:

- Align the team around the LogicCosmo split.

Likely files:

- `LOGICOSMO.md`
- `README.md`
- `docs/OPERATIONS.md`

Acceptance criteria:

- Clear recommended architecture.
- Expert vs public responsibilities documented.
- First implementation phase identified.

Verification:

- `python3 backend/tests/test_qa.py`

### Phase 2: Route And Template Separation

Goal:

- Add public/customer template namespaces without moving expert features yet.

Likely files:

- `backend/api/main.py`
- `templates/public/*`
- `templates/customer/*`
- `templates/shared/*`
- `locales/*.json`

Acceptance criteria:

- Public routes do not show expert nav.
- Expert routes still work.
- Customer and expert base templates are separate.

Verification:

- Template parse checks.
- `python3 backend/tests/test_qa.py`

### Phase 3: Public Landing And Product Page

Goal:

- Create the first public LogicCosmo storefront pages.

Routes:

- `/`
- `/pt-BR`
- `/en`
- `/readings/life-map`

Acceptance criteria:

- Clear beginner-friendly explanation.
- EN/PT copy exists.
- No expert dashboard links.
- Call to action leads to login/account/birth-profile flow.

Verification:

- Template parse checks.
- `python3 backend/tests/test_qa.py`

### Phase 4: Customer Account And Birth Profile Flow

Goal:

- Customer can create/confirm birth data without entering the expert dashboard.

Routes:

- `/account`
- `/birth-profile`

Acceptance criteria:

- Customer sees own profiles/orders only.
- Birth data confirmation is clear.
- Timezone and location are explicit.

Verification:

- Owner-scope smoke checks.
- `python3 backend/tests/test_qa.py`

### Phase 5: Public Checkout And Order Integration

Goal:

- Move purchase flow into customer pages.

Routes:

- `/checkout`
- `/orders/{order_id}`

Acceptance criteria:

- Server-side price only.
- Stripe Checkout opens from public customer flow.
- Return page shows status.
- Paid order can generate.
- Unpaid order cannot generate.

Verification:

- Stripe sandbox manual test.
- `python3 backend/tests/test_qa.py`

### Phase 6: Reading View And PDF Download

Goal:

- Deliver the purchased reading as the actual product.

Routes:

- `/orders/{order_id}/reading`
- `/orders/{order_id}/export.pdf`

Acceptance criteria:

- Reading view uses stored generated content.
- PDF uses stored generated content.
- Customer can download PDF.
- Reading language matches order language.

Verification:

- Stored-content smoke check.
- PDF generation check.
- `python3 backend/tests/test_qa.py`

### Phase 7: Admin/Expert Separation And Hardening

Goal:

- Make customer/public launch safe.

Tasks:

- Add `users.role` / access level.
- Gate expert routes.
- Add admin order view.
- Add audit view for generated readings.
- Hide/remove expert checkout button.
- Harden persistence and backups.

Acceptance criteria:

- Normal customer cannot access expert pages.
- Expert/admin can review orders and readings.
- Paid data is durable and backed up.

Verification:

- Role/access smoke checks.
- `python3 backend/tests/test_qa.py`

## First Safe Coding Task

Recommended first implementation task:

Create the route/template separation foundation without changing customer behavior yet.

Scope:

- Add `templates/public/base_public.html`.
- Add `templates/public/landing.html`.
- Add public landing routes for `/`, `/pt-BR`, and `/en`.
- Keep existing `/dashboard` and expert routes unchanged.
- Do not wire checkout into the public landing yet.
- Do not move existing expert templates yet.

Why this first:

- It creates a visible separation between LogicCosmo and the expert app.
- It is low risk.
- It does not touch the engine.
- It creates a foundation for public marketing copy and i18n.

## Design AI Handoff

Use design tooling to explore the public LogicCosmo experience, not the expert dashboard.

Design brief for external tools:

- Product: LogicCosmo, a public Vedic astrology reading storefront.
- Primary offer: Life Map Reading / Mapa de Vida Vedico.
- Audience: beginners, especially Brazilian users familiar with Western astrology or sun-sign astrology.
- Tone: simple, premium, warm, spiritually intelligent, not occult clutter, not generic SaaS.
- Goal: explain the value of a Vedic life map, collect birth data, guide checkout, and deliver a polished stored reading.
- Avoid: raw charts, dense technical navigation, unexplained Sanskrit, expert-only tools, generic AI-spiritual filler.
- Required languages: English and Brazilian Portuguese.
- First pages to design:
  - Public landing page.
  - Life Map product page.
  - Birth-data confirmation page.
  - Checkout review page.
  - Stored reading view.

Recommended design output format:

- Start with static mockups or HTML/CSS concepts.
- Keep implementation compatible with FastAPI + Jinja templates.
- Avoid requiring a heavy frontend framework unless there is a strong reason.
- Preserve accessibility, mobile layout, and clear conversion flow.

## Risks Before Real Customers

- SQLite persistence/backups are not sufficient for serious paid scale.
- Customer/expert route separation is not complete yet.
- Role/access level is not implemented yet.
- PDF export is not implemented yet.
- Public reading page is not implemented yet.
- The expert dashboard still contains a checkout panel from the proof-of-concept flow; it should be hidden or moved after public checkout exists.
- Firebase authorized domains must include `logicosmo.com` before domain launch.
- Stripe webhook URL must be changed carefully when moving from Railway URL to `logicosmo.com`.
- Email sending/reply-to from `info@logicosmo.com` is not configured yet.

## What Is Needed Before Coding Public Product

From product/business:

- Confirm whether `logicosmo.com` should default to Portuguese or locale auto-detection.
- Confirm initial public brand tone: mystical, scientific, premium, minimalist, or editorial.
- Confirm whether the expert app should remain at the Railway URL, `/expert`, or a future subdomain such as `expert.logicosmo.com`.
- Confirm whether users should be able to generate immediately after payment or whether there should be an optional review delay.
- Confirm customer support email behavior for `info@logicosmo.com`.

From infrastructure:

- DNS readiness for `logicosmo.com`.
- Firebase authorized domain setup for `logicosmo.com`.
- Stripe webhook migration timing.
- Decision on SQLite hardening vs managed Postgres before real paid launch.

## Recommended Architecture Summary

Use the same FastAPI app now, with separate public/customer routes and templates, plus explicit role gates for expert/admin routes. Keep the existing app as the internal engine room. Build LogicCosmo as the public storefront and reading delivery layer on top of the current trusted calculation and order infrastructure. Revisit separate app/service deployment after the public journey, PDF delivery, and access-control model are stable.
