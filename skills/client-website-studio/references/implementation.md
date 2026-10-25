# Engineering rules for compact static sites

## Layout

The project folder itself is the website. There is no `site/` wrapper.

```text
index.html     the entire bilingual website, with every runtime asset embedded
```

Beside these sit the private working folders (`client/`, `brand/`, `concepts/`, `review/`, `feedback/`, `handover/`, `preview/`), which are never shipped.

- Keep complete Arabic and English semantic content in lang/dir containers in index.html. Share inline CSS and JavaScript. Use unique IDs across both languages; never fetch translations or asset files.
- The one page: `<!doctype html>`, `<html lang="ar" dir="rtl">` or `<html lang="en" dir="ltr">`, charset, viewport, one meaningful client-specific title, a meta description, a sensible heading order, and a canonical link once the final URL is confirmed. Follow seo.md; do not fabricate alternate language URLs.
- Skip-to-content link, `<main id="main">`, proper landmarks, real buttons and anchors. Navigation, WhatsApp, email and phone links must do exactly what their labels say.
- Give each top-level `<header>`, `<section>` and `<footer>` a `data-section` attribute with a short name in the page's language (see `review-rounds.md`). Feedback uses these names.

## Paths and links

- Use `#section-id` for navigation and language links. No local page or download links. External contact/map links are allowed; external runtime resources are not.
- Phone links use the country code: `tel:+218…`. WhatsApp links use digits only: `https://wa.me/2189…`, with no `+`, spaces or leading zero.

## Assets and third parties

- Embed assets: CSS in `<style>`, JavaScript in `<script>`, SVG inline or in data URIs, compressed raster images and licensed fonts as data URIs. Inline required licence notices; keep original files privately in brand/. Use system fonts when embedding a font is unnecessary. No CDN, @import, fetch, remote scripts, remote images or iframe widgets.
- No analytics, trackers, session replay, cookies, remote widgets or other third-party requests without the client's explicit permission and a disclosure.
- No contact form that pretends to submit without a real endpoint. Use clearly labelled `mailto:`, call or WhatsApp links instead. No secrets or client data in front-end files.
- Use `textContent`, not `innerHTML`, for dynamic text. No `eval`, inline event strings or generated code. Add JavaScript only for behaviour that is truly needed.
- No unnecessary folders, config files, package manifests, source maps, tests, unused assets or duplicate files in the website. Never write a `web.config` or `.htaccess` for the host; the packager does not ship them.
- The root `index.html` is the full bilingual landing page, never an empty file, a placeholder or a redirect-only page.
- Never put a local computer path (`C:\...`, `file:///`) or a path into a working folder in any file.
- For tiny sites, avoid elaborate caching or service workers. Version a file name only when a change must bypass caches.

## Browser storage

Default to **no browser storage**. Use same-page language anchors; do not require storage for language selection. If storage is truly justified:

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
