# Distinctive, trustworthy design

Before building, write a short internal design rationale in `PROJECT-STATUS.md` under the technical notes: industry, audience, trust cues, tone, one distinctive visual element, content order, colour pairing, type pairing, image strategy, navigation and footer. Show the marketer two or three directions in everyday words, not design jargon.

## Brand inputs come from the marketing team

- Use the logo, colours, fonts and photos the marketing team provides. Build the website palette from their colours.
- If they provide no colours, choose a restrained palette and call it "the website colours", not a brand identity.
- Never draw a logo or create a brand identity. If the logo is missing, use the company name as text and list the logo as pending.

## Avoid AI sameness

- Do not reach by reflex for a big centred hero, gradient blobs, three equal cards, fake social proof, huge pill buttons, identical stock photos, or a lightly tinted background on every section.
- Match the layout to the business: law and accounting firms restrained and credible; workshops and industry led by real work and photos; clinics reassuring, clear and careful with claims; retailers product-led; logistics operationally clear.
- Choose one distinct motif (a grid, a photo crop, a typographic scale, editorial asymmetry, a local architectural detail) and stay coherent.
- Make content useful: a clear description, specific services, location, easy contact and appropriate company details. Never pad with unsupported claims.

## A practical design system (adapt per client)

- Tokens as CSS custom properties for colour, background, text, muted text, borders, spacing, font families, control height, radius and focus outline. No repeated magic values.
- Body text 16–18px with 1.5–1.8 line height; fluid headings with `clamp()` where useful. Contrast at least WCAG AA: 4.5:1 for normal text, 3:1 for large text. Keyboard focus always visible.
- Touch targets about 44×44 CSS px where feasible; link and button states obvious. No icon-only controls without a label.
- Comfortable reading width (about 65–75 characters for long passages), generous spacing, clear hierarchy, predictable header and footer.
- Navigation never clips. Menus open and close by click or tap, work with the keyboard and Escape, and set `aria-expanded`. No hover-only menus.
- Fonts: system font stacks, or self-hosted font files with an open licence. Arabic families on Google Fonts (for example IBM Plex Sans Arabic, Noto Kufi Arabic, Cairo, Tajawal, Almarai) are open-licensed; ship only the `woff2` files you use and include the licence file. Never ship a font without permission. Test Arabic shaping with mixed Latin text and numbers.
- Use logical properties (`padding-inline`, `margin-inline`, `text-align: start`) instead of duplicating RTL styles.
- Media gets `max-width: 100%`; no horizontal overflow; no fixed heights on content; grid and flex layouts that wrap with their content.
- Test 320, 360, 390, 768, 1024 and 1440 px widths in RTL and LTR, with long company names, long translations and 200% text zoom.
- Motion is optional and subtle, and honours `prefers-reduced-motion`.
- Use real client photos or properly licensed images. Informative images get meaningful `alt` text; decorative ones get empty `alt`. Use descriptive file names, `loading="lazy"` below the fold, and `width`/`height` to avoid layout shifts.

## External design skills

UI UX Pro Max, the frontend-design plugin and Vercel's web design guidelines (links in `SKILL.md`) are useful for ideas. If any of them pushes Tailwind, React, libraries or heavy animation, ignore that part and take only the design advice.
