# From the marketing team's material to a brief

The marketing team runs intake with the client and supplies the brand assets: logo, colours, photos and any identity work. Your job is to organise what they give you, check it, and ask only for what is missing.

## Read the inbox

Anything can arrive in `client/inbox/`: form exports, typed notes, WhatsApp screenshots, PDFs, a company profile, logo files, photos or registration certificates. Read all of it, images included. Then:

1. Create `client/brief.md` from `<skill>/assets/brief-template.md` and fill one row per fact: the value, its source (file name, or "marketer in chat") and its status.
2. Use three statuses:
   - **مؤكد / confirmed:** taken from client material as written.
   - **يحتاج تأكيد / needs confirmation:** anything you drafted, translated or rephrased, and any fact where sources disagree.
   - **ناقص / missing:** needed but not provided.
3. Copy files into place without changing the originals: logo and brand files to `brand/`, usable photos to `brand/photos/`, registration papers to `client/documents/`.
4. If a registration certificate is present, compare the legal name (Arabic and English) and the registration numbers with the rest of the material. Report any difference and never quietly pick one, because a bank compares the website with official records.
5. Do not read or keep personal identity documents (passports, national ID cards), bank statements or passwords. If one arrives, tell the marketer it does not belong in the folder and ask them to remove it.

## What the website needs

- Official company name in Arabic and English, exactly as approved. Never invent a transliteration.
- What the company does: a one-sentence summary, services or products, audience, and area served.
- Contact details: phone and WhatsApp with the country code (+218…), a business email on the client's domain, the address or area, a map link if public, and working hours.
- Social media accounts, with exact URLs.
- Any registration details the client wants shown, exactly as on the documents.
- Which language opens first, and who approves each language.
- The main action for visitors: call, WhatsApp, email or visit.
- The domain spelling and the mailbox names to show, such as info@.
- Logo, colours, photos and permission to use them, all from the marketing team.

## Asking for gaps

- Send the marketer one grouped, numbered list in plain Arabic that they can forward to the client on WhatsApp. Do not ask for anything the brief already answers.
- Keep design work moving while optional facts are missing. In pages, mark unknown values only as `[[NEEDS: what is missing]]`.
- If brand assets are missing, list them as a task for the marketing team. Do not create a logo or an identity. Until the logo arrives, show the company name as text.
- Use customer language: "How should customers contact the company?", not "What is the CTA?"

## Fact sheet before release

Before building the release ZIP, give the marketer a one-page summary of every fact that will be public, in each site language, as text or an image they can send to the client. When the client approves, record who approved, when and through which channel in `PROJECT-STATUS.md`, and ask the marketer to save the screenshot in `client/approvals/`.
