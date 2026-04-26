# LogicCosmo Design System

## Overview

**LogicCosmo** is a public-facing Vedic astrology reading platform that sells polished, beginner-friendly life map readings. The product translates complex Vedic astrology into warm, guided, human-readable insights for everyday users — not experts.

**Primary Product:**
- English: *Life Map Reading*
- Portuguese: *Mapa de Vida Védico*

**Audience:** Beginners, especially Brazilian users who may only know Western or sun-sign astrology. Spiritually curious, not technically trained.

**Core Message:** "This is not just a chart. It is a guided life map based on your birth data, planetary periods, and Vedic astrology logic."

---

## Sources

This design system was created from scratch based on a detailed product brief. No external codebase or Figma file was provided. All visual decisions are original derivations of the brand direction described below.

If a codebase or Figma is later attached, this README should be updated with exact paths and links.

---

## Products / Surfaces

| Product | Description |
|---|---|
| **LogicCosmo.com** | Public marketing + purchasing site (landing, product page, birth form, checkout, reading view) |
| **Internal Expert Dashboard** | Dense astrology cockpit (NOT designed here — out of scope) |

---

## User Journey

1. Public landing page
2. Life Map Reading product page
3. Signup / login
4. Birth data confirmation
5. Checkout review
6. Payment
7. Order status
8. Stored reading view
9. PDF download

---

## Pricing (Brazil Launch)

| Tier | Price |
|---|---|
| First 100 readings | R$ 10,99 |
| Next 100 readings | R$ 59,99 |
| Standard | R$ 99,99 |

---

## CONTENT FUNDAMENTALS

### Tone
- **Warm, premium, spiritually intelligent** — never occult, never clinical
- Like a knowledgeable friend explaining your birth chart over coffee
- Avoids jargon unless immediately explained in plain language
- Never condescending; assumes curiosity, not expertise

### Voice
- **Second person** ("your chart", "you were born", "your life map")
- Sentences are conversational but measured — not chatty, not corporate
- Confident and clear. No hedging ("might", "perhaps", "it's possible that")
- English is formal enough to feel premium; Brazilian Portuguese is warm and direct

### Casing
- Headlines: Title Case in English, Sentence case in Portuguese
- CTAs: Title Case ("Start Your Reading", "Ver Meu Mapa")
- Body: Sentence case
- Avoid ALL CAPS except for small label tags

### Emoji
- **Not used** in product UI. May appear sparingly in social content only.

### Sanskrit / Technical Terms
Always explained in parentheses on first use:
- Mahadasha (your major planetary life period)
- Antardasha (sub-period within the major period)
- D1 / Rashi Chart (your main birth chart)
- Bhava Chalit (house-adjusted chart showing lived reality)
- Atma Karaka (soul significator — what your soul came to learn)
- Amatya Karaka (career significator — your natural work path)

### Copy Examples
- "Understand your life through the lens of Vedic astrology — the world's most precise birth chart system."
- "You are currently in a Saturn Mahadasha (major life period) — a 19-year arc of discipline and karmic reckoning."
- "This is not a prediction. It is a map."

---

## VISUAL FOUNDATIONS

### Color System
- **Background:** Warm cream (`#FAF7F2`) — light, editorial, premium feel
- **Surface:** Off-white (`#F3EFE8`) for cards and panels
- **Deep Indigo:** `#1B1F4A` — primary brand color, headers, anchors
- **Midnight Blue:** `#0F1235` — darkest tone, used for full-bleed hero sections
- **Gold / Saffron:** `#C8922A` — primary accent, CTAs, highlights
- **Warm Gold Light:** `#F0C96A` — secondary accent, star glows, decorative
- **Muted Sage:** `#7A8C7E` — neutral text, secondary info
- **Error:** `#C0392B`
- **Success:** `#2D7A4F`

### Typography
- **Display / Headings:** *Cormorant Garamond* (serif, editorial, premium feel) — Google Fonts
- **Body / UI:** *DM Sans* (humanist sans-serif, clear, warm) — Google Fonts
- **Mono / Data:** *DM Mono* (for birth data, chart numbers) — Google Fonts

Font substitution note: These are Google Fonts. If the brand commissions custom typefaces, update this section.

### Spacing
- Base unit: `8px`
- Scale: 4, 8, 12, 16, 24, 32, 48, 64, 96, 128px
- Section padding (mobile): 48px vertical
- Section padding (desktop): 96px vertical

### Backgrounds
- **Light pages:** Warm cream (`#FAF7F2`) with subtle noise texture overlay (5% opacity)
- **Dark hero sections:** `#0F1235` with radial star-field gradient and faint orbital SVG line art
- **Cards:** `#F3EFE8` with `1px` border (`#E5DDD0`) and soft drop shadow
- No harsh full-bleed photography — illustrated/gradient treatments preferred

### Gradients
- Hero gradient: `radial-gradient(ellipse at 60% 40%, #2A2E6E 0%, #0F1235 70%)`
- Gold shimmer: `linear-gradient(135deg, #C8922A, #F0C96A, #C8922A)`
- Subtle card warm: `linear-gradient(180deg, #FAF7F2 0%, #F3EFE8 100%)`

### Animation
- Easing: `cubic-bezier(0.25, 0.1, 0.25, 1)` (ease) for most transitions
- Duration: 200ms for hover states, 350ms for panel transitions, 600ms for page entrances
- Fade + subtle upward translate (`translateY(8px) → translateY(0)`) for entrance animations
- No bounces. No spring physics. Measured and calm.

### Hover States
- **Buttons:** Gold darkens 10%, slight shadow lift (`box-shadow` grows)
- **Links:** Underline appears, color shifts to gold
- **Cards:** `box-shadow` grows, `translateY(-2px)`, 200ms ease
- No opacity-only hovers

### Border Radius
- **Small (tags, badges):** `4px`
- **Medium (inputs, buttons):** `8px`
- **Large (cards, panels):** `16px`
- **Pill (CTAs):** `999px`
- No fully square corners anywhere

### Shadows
- **Card resting:** `0 2px 8px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04)`
- **Card hover:** `0 8px 24px rgba(0,0,0,0.10), 0 2px 4px rgba(0,0,0,0.06)`
- **Modal / Drawer:** `0 24px 64px rgba(0,0,0,0.18)`
- **Input focus ring:** `0 0 0 3px rgba(200,146,42,0.25)`

### Imagery
- Warm, earthy color grading — no cold blue filters
- Cosmic imagery is abstract: star fields, orbital rings, planetary glows
- No literal zodiac wheel diagrams in marketing
- No stereotypical "crystal ball / horoscope" imagery
- Illustrations use the brand palette (cream, indigo, gold)

### Layout Rules
- Mobile-first. Breakpoints: 390px / 768px / 1280px
- Max content width: `1140px`, centered
- Nav: fixed top, transparent → cream on scroll, with blur backdrop
- Reading sections use alternating cream/white backgrounds to create rhythm

### Iconography
- See ICONOGRAPHY section below

---

## ICONOGRAPHY

No proprietary icon set was provided. The brand uses **Lucide Icons** (stroke-based, clean, 1.5px stroke weight) via CDN.

Usage rules:
- Always 20px or 24px size
- Stroke color matches text color of context
- Never filled icons — stroke only
- Paired with labels always; icons never stand alone without text
- Do not use emoji as icons in product UI

CDN: `https://unpkg.com/lucide@latest/dist/umd/lucide.min.js`

Key icons used:
- `star` — premium quality signals
- `map` — life map metaphor
- `calendar` — birth date input
- `clock` — birth time input  
- `map-pin` — birth place input
- `download` — PDF download
- `check-circle` — confirmation states
- `lock` — secure checkout
- `chevron-right` — navigation

---

## File Index

| File / Folder | Description |
|---|---|
| `README.md` | This file — brand overview and all design foundations |
| `colors_and_type.css` | CSS custom properties for all colors, type, spacing, shadows |
| `assets/` | Logo SVGs, brand marks, decorative SVGs |
| `preview/` | Design system card HTML files (shown in Design System tab) |
| `ui_kits/logicosmo/` | Full UI kit for the public LogicCosmo.com site |
| `SKILL.md` | Agent skill manifest |

---

## UI Kits

| Kit | Path | Description |
|---|---|---|
| LogicCosmo Public | `ui_kits/logicosmo/index.html` | Landing page + reading purchase flow |

### UI Kit Screens (click through via breadcrumb at bottom)

| Screen | Component File | Description |
|---|---|---|
| Landing | `LandingPage.jsx` | Hero, What You Receive, How It Works, Why Vedic, Pricing, FAQ, CTA |
| Product | `ProductPage.jsx` | Reading product detail page with purchase card |
| Birth Data | `ProductPage.jsx` (BirthDataForm) | Birth date/time/place form with step indicator |
| Checkout | `CheckoutAndReading.jsx` (CheckoutPage) | Order review, payment methods, confirmation |
| Reading | `CheckoutAndReading.jsx` (ReadingView) | Full stored reading view with expandable sections |

### Shared Components (`Shared.jsx`)
- `<Nav dark>` — fixed top nav, light and dark variants
- `<Footer>` — full site footer with links
- `<Btn variant>` — primary, secondary, ghost, dark, inverse
- `<Label>` — overline/tag label
- `<SectionHeading label title subtitle>` — reusable section header block
- `<LC_MARK>` — orbital SVG logo mark
