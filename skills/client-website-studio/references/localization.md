# Arabic and English

- Both languages are complete, first-class experiences. Which language opens first is a content decision confirmed with the client; do not assume English.
- Set `lang` and `dir` on every page (`ar` with `rtl`, `en` with `ltr`).
- Each page has a visible language switch that links to the equivalent page by file name (`../en/index.html`), and to the equivalent section where practical. Label it in the target language's own script: `English`, `العربية`. No flags.
- Translate everything visible plus metadata: navigation, buttons, footer, copyright, accessible labels, meaningful `alt` text, form labels if any, titles and descriptions. Keep names and regulated terms exactly as approved.
- Isolate left-to-right fragments inside Arabic text: phone numbers, emails, URLs, registration numbers and dates (`<bdi>` or `dir="ltr"`). Check punctuation and order visually.
- Use CSS logical properties and careful flex direction. Do not mirror photos, logos, maps or directional brand marks.
- Keep labels short in both languages, and test long translations on narrow screens.
- Use separate pages (`/ar/`, `/en/`), never machine translation in the browser or a toggle that swaps only the headings.
- Change both languages together. When a review note edits one language, ask whether the other needs the same change.
- If one language lacks confirmed content, do not call the site ready for a bilingual launch.
