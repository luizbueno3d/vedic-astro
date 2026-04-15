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

Main file:

- `backend/data/profiles.db`

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
