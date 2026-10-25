# Automatic, truthful search setup

Do this for every landing page without asking non-technical staff for SEO settings or keyword lists.

1. Read client/brief.md and approved materials. Use the confirmed Arabic/English business name and known spellings, actual services/products and confirmed city/service area. A name alone does not prove an industry or location: never invent them. Ask one plain business question only when essential business information is missing.
2. Prioritise Arabic search phrases and Arabic default title/description; include useful English brand spellings naturally. Derive a compact Arabic and English search phrase set: exact name, natural name variants, actual service, and service + confirmed location. Record the choices and their source in client/brief.md. Never target competitors, irrelevant places or unsupported claims.
3. Write a useful client-specific title and meta description directly in head. Include the name and strongest confirmed service/location naturally. Write meaningful headings and visible copy using these terms without repetition or hidden keyword blocks. Translate metadata for the optional language switch, retaining static default-language metadata when JavaScript fails.
4. Include og:title, og:description, og:type=website and appropriate locale information. Add og:url and a canonical only after the public URL is confirmed. Never use localhost, the agency preview domain or invented domains as the final URL. A share image must be an existing publicly hosted approved image: data URIs are not reliable social preview images; omit og:image if none exists rather than create another asset file.
5. Include valid application/ld+json using Organization, or a truthful specific LocalBusiness type when the brief supports it. Use actual name/alternateName, url, telephone, address and sameAs only where confirmed. Omit missing facts. No invented reviews, ratings, opening hours, licences, prices or awards. Structured data must match visible content. Validate JSON and schema meaning; tag presence alone is not validation.
6. Keep the release crawlable: meaningful static text, working anchors, descriptive image alt text, no noindex or nofollow left over from previews. Keep preview noindex. Use the one real canonical URL; do not create robots.txt, sitemap.xml or any other deployable file under the single-file contract. Host-level robots rules and search-engine submission are separate, explicitly approved hosting tasks.
7. Review business relevance and both languages manually. Record metadata, confirmed canonical or pending URL, checks and outstanding search-submission tasks in handover/quality-report.md. The audit checks metadata presence; it cannot judge relevance, translation quality, rankings, schema eligibility or indexing.

Meta keywords are optional for tools that request them, never a substitute for useful content. Google ignores the keywords meta tag. Do not sell keyword tags as ranking work or promise placement/indexing.

One-file trade-off: Google recommends separate URLs for language versions. This kit deliberately uses one URL with bilingual HTML and a user-operated switch. Google may not index both versions independently. Never create separate pages to solve this or claim fragment links are separate indexed translations; explain the limitation briefly in handover.

Official sources (recheck when behavior matters):
- https://developers.google.com/search/docs/crawling-indexing/special-tags
- https://developers.google.com/search/docs/specialty/international/managing-multi-regional-sites
- https://developers.google.com/search/docs/appearance/structured-data/organization
- https://developers.google.com/search/docs/appearance/structured-data/local-business

Missing content: always ask staff in plain Arabic for the specific missing material. If they say no, unavailable or not needed, omit the whole affected item/section and its navigation in both languages, including dependent buttons and structured data fields. Never display missing/pending text, placeholder images, empty cards or coming-soon substitutes on the landing page, even during previews. Keep outstanding notes privately; do not repeat a question already declined. Essential launch blockers are discussed privately rather than filled with invented facts.
