# Client website project

This folder is one client's website project, run by a non-technical marketer. The website files (`index.html` with both languages and all assets embedded) sit directly in this folder. Working folders (`client/`, `brand/`, `concepts/`, `review/`, `feedback/`, `handover/`, `preview/`) are private and are never published.

1. Read `PROJECT-STATUS.md` before anything else.
2. Use the `client-website-studio` skill from your user-level skills folder. If it did not load automatically, read its `SKILL.md` now and follow it. Never copy the skill or the kit into this folder; if you find a copy here, run the skill's `normalize_project.py`.
3. Talk to the marketer in Arabic, in plain words, one decision at a time. Never show code unless they ask.
4. Never ask for passwords. Never publish anything without explicit approval.
5. Update `PROJECT-STATUS.md` after every stage and every review round.
6. When you finish any work that changes the site, rebuild the preview, start the local preview server yourself without asking, and send the marketer the localhost link. They cannot run commands.
7. The only thing handed over for publishing is `handover/DEPLOY-READY.zip`, built by the skill's packaging script.

Always build exactly one root index.html with complete Arabic and English content and all CSS, JS, images, icons and fonts embedded. Never create extra pages or an assets folder. Automatically derive truthful client-specific search phrases and metadata from approved names, services and location; follow references/seo.md in the installed skill. Do not ask staff for SEO configuration.

Arabic is the primary experience by default: html lang="ar" dir="rtl", Arabic-first headings, navigation, title, description and search phrases. Prioritise natural Libyan Arabic business wording, readable Arabic typography, correct shaping and punctuation, RTL keyboard flow and mobile layout. English remains complete in the same file. Only change the default if the client explicitly requests it. Never transliterate Arabic copy or infer the business category from its name.

Missing content: always ask staff in plain Arabic for the specific missing material. If they say no, unavailable or not needed, omit the whole affected item/section and its navigation in both languages, including dependent buttons and structured data fields. Never display missing/pending text, placeholder images, empty cards or coming-soon substitutes on the landing page, even during previews. Keep outstanding notes privately; do not repeat a question already declined. Essential launch blockers are discussed privately rather than filled with invented facts.
