# Engineering rules for compact static sites

## Layout

```text
site/
  index.html              short language choice page, or the approved default language
  ar/index.html
  en/index.html
  assets/css/site.css
  assets/js/site.js       only when needed
  assets/images/...
  assets/fonts/...        self-hosted fonts plus their licence file
  favicon.svg             only if the marketing team supplied a mark
```

- Each language page owns its semantic HTML and approved text. Shared CSS and JS carry shared presentation and behaviour. Repeating localised HTML structure is acceptable for no-build hosting; duplicating logic, styles or large pasted blocks is not.
- Every page: `<!doctype html>`, `<html lang="ar" dir="rtl">` or `<html lang="en" dir="ltr">`, charset, viewport, a unique title, a meta description, a sensible heading order, and canonical/hreflang links once the final URLs are known.
- Skip-to-content link, `<main id="main">`, proper landmarks, real buttons and anchors. Navigation, WhatsApp, email and phone links must do exactly what their labels say.
- Give each top-level `<header>`, `<section>` and `<footer>` a `data-section` attribute with a short name in the page's language (see `review-rounds.md`). Feedback uses these names.

## Paths and links

- Use **relative paths only** for local files and pages: `assets/css/site.css`, `../en/index.html`. Never start a local path with `/`. Relative paths keep the site working inside the agency's preview subfolder and when opened straight from a folder. The audit treats a leading `/` as an error.
- Link to pages by file name (`../en/index.html`, not `../en/`). A folder link opens a file list when the preview is opened from disk.
- Phone links use the country code: `tel:+218…`. WhatsApp links use digits only: `https://wa.me/2189…`, with no `+`, spaces or leading zero.

## Assets and third parties

- Keep assets local wherever practical. If Bootstrap is truly justified, ship the licensed files locally instead of using a CDN, and never add it for a handful of simple sections.
- No analytics, trackers, session replay, cookies, remote widgets or other third-party requests without the client's explicit permission and a disclosure.
- No contact form that pretends to submit without a real endpoint. Use clearly labelled `mailto:`, call or WhatsApp links instead. No secrets or client data in front-end files.
- Use `textContent`, not `innerHTML`, for dynamic text. No `eval`, inline event strings or generated code. Add JavaScript only for behaviour that is truly needed.
- No unnecessary folders, config files, package manifests, source maps, tests or unused libraries inside `site/`.
- For tiny sites, avoid elaborate caching or service workers. Version a file name only when a change must bypass caches.

## Browser storage

Default to **no browser storage**. With separate `/ar/` and `/en/` pages, a language preference does not need storage; link directly. If storage is truly justified:

1. Define a specific, non-sensitive purpose and value type.
2. Use one versioned key, for example `companySite.language.v1`.
3. Wrap every read and write in `try/catch`, because storage can be blocked.
4. Validate what you read against the allowed values (for example `ar`, `en`) and fall back to the page language.
5. Never store credentials, identity data, messages, tracking data or anything sensitive.
6. No generic storage helper for one simple preference.

## Performance and reliability

- Sensible image formats and sizes. Compress large originals; aim for under about 300 KB per photo. Lazy-load only images below the fold.
- No autoplay video or heavy carousels by default. Pages must show meaningful content even if JavaScript fails.
- Small reusable CSS tokens and utilities where repetition needs them; no over-engineered abstractions.
- Remove duplicated declarations, unreachable JS, needless listeners, unused files and heavy network requests.
- A static site never needs a database or server. Do not invent one.
