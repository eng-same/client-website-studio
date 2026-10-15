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

## Quality bar for every site

Judge each screenshot against these principles before showing it, and fix what fails.

- **No template look.** If the design could belong to any business with the name swapped, it is not finished. Do not reach for the effects and layouts that mark generated sites: decorative backgrounds, glows, ghost graphics, floating widgets, uniform rounded cards, stacked badges and chips. Get character from one idea tied to what this business does, from type scale and from composition.
- **A clear first screen.** One message, one main action, one visual idea, balanced in the space. No large empty areas, no loose blocks of data floating in a corner, no crowding of every available element. If a visitor cannot grasp it in a few seconds, remove things.
- **Nothing overflows.** Run `check_layout.py` after every preview build; any element wider than the screen, clipped text or sideways scrolling at 320, 360, 390, 768, 1024 or 1440 px is a failure to fix before showing anything. Non-technical staff cannot diagnose it, so it must never reach them.
- **No repetition.** Do not repeat the same decoration, icon, shape or call-to-action on every item or in every section, and never show the same information twice on one page (for example contact details in both a contact section and the footer, or the same button in three places). Each fact and each action has one best place. One treatment per job. A plain text link needs no ornament.
- **No overlap.** Nothing may cover other content or controls at any width. Check that fixed or floating elements never hide a link, button or text.
- **Restraint in controls.** Header, buttons, language switch and footer are quiet, clear and consistent with the rest of the page: simple shapes, obvious states, visible focus, readable labels. The language switch names the other language in its own script and is never a novelty control.
- **A real footer.** Not a single line: name, short description, section links, language link and copyright, plus contact details only when the page has no contact section. Only confirmed facts and accounts.
- **RTL and LTR, checked by eye.** Every directional element must be verified in both languages from the screenshots, not assumed: arrows and chevrons follow the reading direction, direction-implying icons are mirrored, spacing and borders use logical properties, text and lists align to the start side, and numbers, phone numbers and Latin names keep their own order. Compare both languages and fix every mismatch before the marketer sees the preview.
- **Distinctive, not decorated.** One business-specific idea built in CSS/SVG, strong type contrast and clear hierarchy beat effects.
