# Arabic and English in one file

- Deliver exactly root index.html. Never create language folders or another page.
- Default to Arabic with html lang="ar" dir="rtl" unless the client explicitly chooses otherwise. Treat Arabic as the primary review target, including typography, natural wording, punctuation, mobile navigation and search metadata.
- Include all approved text for both languages directly in HTML, not remote JSON, machine translation or JavaScript-only strings. Each complete language container uses lang="ar" dir="rtl" or lang="en" dir="ltr" and a unique ID.
- Provide real in-page anchors to each language container, labelled English and العربية, with matching lang attributes. These must work without JavaScript. An optional inline script may enhance this into a language toggle: hide only after initialization, update html lang/dir, translated accessible labels, title and description; support keyboard use and fragment/history navigation. Test both states. On script failure, both languages remain readable and linked.
- Translate navigation, sections, footer, buttons, alt text and accessible labels. Do not switch only headings. Keep unique IDs across both versions; use one h1 and sensible subsequent headings.
- Isolate phone numbers, emails and other LTR fragments using bdi or dir="ltr". Use CSS logical properties; never mirror logos or photos. Check long text on narrow screens.
- Do not auto-redirect visitors based on location or browser language. Do not use browser storage by default.
- Update both languages together when applying feedback; record genuinely missing translated content as pending. Missing language content or in-page links blocks release. --single-language requires explicit client agreement and never permits extra files.
- Read seo.md for the indexing trade-off of one bilingual URL. Do not promise independent language indexing or add fake hreflang routes.

Missing content: always ask staff in plain Arabic for the specific missing material. If they say no, unavailable or not needed, omit the whole affected item/section and its navigation in both languages, including dependent buttons and structured data fields. Never display missing/pending text, placeholder images, empty cards or coming-soon substitutes on the landing page, even during previews. Keep outstanding notes privately; do not repeat a question already declined. Essential launch blockers are discussed privately rather than filled with invented facts.
