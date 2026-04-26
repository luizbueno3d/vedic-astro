---
name: logicosmo-design
description: Use this skill to generate well-branded interfaces and assets for LogicCosmo — a public Vedic astrology reading platform. Contains essential design guidelines, colors, type, fonts, assets, and UI kit components for prototyping the customer-facing LogicCosmo.com experience.
user-invocable: true
---

Read the README.md file within this skill, and explore the other available files.

If creating visual artifacts (slides, mocks, throwaway prototypes, etc), copy assets out and create static HTML files for the user to view. Import `colors_and_type.css` for all design tokens, and reference the Google Fonts stack: Cormorant Garamond (display/headings), DM Sans (body/UI), DM Mono (data/code).

If working on production code, read the colors_and_type.css token system and apply it to your implementation. Match the warm-cream light theme (#FAF7F2 bg, #1B1F4A headings, #C8922A accent gold) and the dark hero theme (#0F1235 bg).

Key brand rules:
- Headings: Cormorant Garamond, light to regular weight, tight leading
- Body: DM Sans, warm and conversational
- Accent: Gold (#C8922A primary, #F0C96A glow)
- Border radius: pill for CTAs, 16px for cards, 8px for inputs
- No emoji in product UI
- Sanskrit terms always explained in parentheses on first use
- Tone: warm, premium, spiritually intelligent — never occult, never clinical

If the user invokes this skill without any other guidance, ask them what they want to build or design, ask some questions, and act as an expert designer who outputs HTML artifacts or production code, depending on the need.
