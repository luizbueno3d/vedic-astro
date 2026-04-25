# Operations

## Authentication

- Firebase is the production login path
- Required Firebase env vars must exist in Railway
- Authorized Firebase domains must include the Railway hostname in production
- Profile access should always be scoped by owner email from session

## Database

SQLite stores:

- user birth profiles
- owner email / uid association
- account-scoped AI settings
- commercial reading product definitions
- future reading orders, generated readings, and export records

Main file:

- `backend/data/profiles.db`

Commercial schema tables:

- `users`
- `reading_products`
- `reading_orders`
- `generated_readings`
- `reading_exports`

The commercial schema is additive and idempotent. `reading_products` is seeded with the first product, `life_map`, using `ON CONFLICT DO NOTHING` so production edits are not overwritten by deploys.

## AI Settings Persistence

- AI settings are stored per signed-in user in `user_ai_settings`
- API keys are not echoed back into the settings UI
- Re-entering a key replaces the saved one

## Dashboard Exports

There are now two dashboard export paths:

- `/dashboard/export` - compact dashboard snapshot
  - current Mahadasha
  - current Antardasha
  - next upcoming Mahadasha
  - next upcoming Antardasha
  - rest of the dashboard data
- `/dashboard/export-dasha` - full dasha tree export
  - all Mahadashas
  - all Antardashas
  - all Pratyantardashas

## Commercial Reading State

Stripe checkout is wired through hosted Checkout Sessions and a verified webhook. The gate creates pending orders and blocks generation until payment is confirmed by Stripe.

Current authenticated endpoints:

- `GET /reading-products`
- `POST /reading-orders`
- `POST /reading-orders/{order_id}/checkout`
- `GET /reading-orders`
- `GET /reading-orders/{order_id}`
- `POST /reading-orders/{order_id}/generate`

Current public payment endpoint:

- `POST /stripe/webhook`

Current order state flow:

- `pending_payment`
- `paid`
- `generating`
- `complete`
- `failed`
- `cancelled`
- `refunded`

Only `paid` orders are eligible for reading generation. Normal API-created orders remain `pending_payment` until `/reading-orders/{order_id}/checkout` creates a Stripe Checkout Session and `/stripe/webhook` receives a verified paid session event.

Generated reading content is stored in `generated_readings` and later PDF exports should use stored content, not recalculate live for each download.

Required Stripe env vars in Railway:

- `STRIPE_SECRET_KEY`
- `STRIPE_WEBHOOK_SECRET`
- `APP_BASE_URL` or `PUBLIC_BASE_URL`

Webhook setup:

- Add the production `/stripe/webhook` URL in the Stripe Dashboard.
- Subscribe at minimum to `checkout.session.completed`, `checkout.session.async_payment_succeeded`, and `checkout.session.expired`.
- Use the endpoint signing secret as `STRIPE_WEBHOOK_SECRET`.

Campaign pricing is recalculated immediately before Checkout Session creation. Pending orders without a Stripe session do not reserve a campaign slot; pending orders with an active Checkout Session do.

## Commercial Snapshot Generator

The deterministic Life Map snapshot generator is implemented in `backend/engine/commercial_reading.py`.

Authenticated inspection endpoint:

- `/commercial-reading/snapshot/{profile_id}`

Optional query parameters:

- `locale=en`
- `locale=pt-BR`
- `as_of=YYYY-MM-DD`

This endpoint is for internal product verification and future order-generation wiring. It does not call AI, does not require Stripe, does not write `generated_readings`, and does not create PDF exports.

## Railway

- App URL has been `https://web-production-db3d.up.railway.app`
- Deploys are triggered from `main`
- If a push does not appear live, force a Railway rebuild with an empty commit

## Common Production Failure Modes

### Firebase auth enabled but Google sign-in fails

- Usually `auth/unauthorized-domain`
- Fix in Firebase Console -> Authentication -> Settings -> Authorized domains

### Login succeeds but app loops back to login

- Usually auth gate / session mismatch
- Confirm signed cookie and session owner are both set correctly

### Dashboard 500 after first login

- Often means the account has no profiles yet or session handling regressed

### AI 429 / provider busy

- OpenRouter free models now retry with backoff and fallback
- If still noisy, switch provider/model

## Current Important Product Decisions

- D1 stays primary; D9/BCC/Jaimini refine, not override
- Dashboard should be informative but not overwhelming
- Full dasha verbosity belongs in dedicated timing surfaces and dedicated exports
- AI is page-aware and should help interpret the current screen, not behave like a generic chatbot

## Known Oddities

- There is still an unrelated untracked file in repo root named `=1.0`
- KP/BCC remains a sensitive area and should be verified carefully whenever changed
