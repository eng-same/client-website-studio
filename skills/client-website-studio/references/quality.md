# Quality gates: test what is actually built

## Every project

1. **Source audit.** `audit_site.py .` (release mode). Fix every error and read every warning. It is a heuristic source check, not a browser test or a compliance certificate.
2. **Browser review.** If you have a browser or screenshot tool, open every page at 320, 360, 390, 768, 1024 and 1440 px. Check navigation, footer, typography, image crops, horizontal scrolling, contact links, the language switch, and RTL/LTR. Try the mobile menu with mouse and keyboard, and text at 200% zoom. Screenshots must come from the real running pages, never imagined ones.
3. **Interactions.** Links resolve; `tel:` uses the approved number with +218; `mailto:` uses the approved address; WhatsApp and map links point to the right place. No fake form submissions or dead controls.
4. **Accessibility.** Keyboard order and visible focus, contrast, heading hierarchy, `alt` text, skip link, touch targets, reduced-motion support where motion exists.
5. **Performance.** Image sizes, script size, external calls and loading behaviour. Use Lighthouse or another tool if available, and report scores only if you measured them.
6. **Content.** Both languages complete and spelled correctly, approved business facts only, correct contact links, no `[[NEEDS]]` markers, no filler and no compliance claims.
7. **Security and privacy.** No passwords, credentials, sensitive storage, personal documents, unnecessary tracking or remote scripts. No form that submits nowhere.
8. **Packaging.** `handover/DEPLOY-READY.zip` has `index.html` at its root, includes every needed asset, and contains no skill, source-only, backup, report, preview or private files. `package_site.py` builds it from the website files only, then `verify_zip.py` logic runs on the finished ZIP (extract, audit, serve over HTTP) and the ZIP is deleted if anything fails.
9. **Live check.** After the host publishes, `check_live.py https://DOMAIN/ --zip handover/DEPLOY-READY.zip` must pass before anyone says the site is published.

## What the audit checks

Errors block packaging; warnings need a human look.

| Area | Errors | Warnings |
| --- | --- | --- |
| Pages | Missing root `index.html`, an empty, placeholder or redirect-only root page, missing `lang`, wrong `dir` for `ar`/`en`, title count not 1, image without `alt`, dead links (`#`, empty, `javascript:`), a missing language page or language switch (release) | Missing doctype, viewport, `<main>` or a single `<h1>`; duplicate ids; sections without `data-section` |
| Structure | The website inside a wrapper folder (`site/` ...) or a second copy of it, skill or agent files inside the project | Server configuration files (never shipped) |
| Files and paths | Broken local references in HTML or CSS, paths leaving the project folder, paths starting with `/`, references into working or wrapper folders, local computer paths, secrets, private keys, non-static source files, duplicate files and unused assets (release) | External resources, folder links, hidden files, PDFs, large images |
| Content | Central Bank compliance or approval wording; in release mode, `[[NEEDS]]` markers | Other placeholder text, any mention of the Central Bank, free webmail addresses, phone links without +, malformed WhatsApp links |
| Preview leftovers | `noindex` tags in release mode | — |

## Decision

- **Block** on wrong contact details, a broken main journey, sensitive content, a broken language, missing pages or assets, unapproved business claims, major layout breakage, or missing client approval.
- **Warn** on untested screen sizes, partly completed browser tests, missing optional search metadata, or images not fully optimised. Be transparent about each.
- Record what was tested, when, by whom and what remains unverified in `handover/quality-report.md`. Never say "passed" for a check you did not run.
