# Review rounds: feedback without code

Marketers judge what they see and never open code. Every round ends with something they can look at and a saved version they can return to.

## Section names

Each top-level `<header>`, `<section>` and `<footer>` carries a `data-section` name in the page's language. Use the same names in chat, in the status file and in screenshots.

- Arabic: الشريط العلوي · الواجهة الرئيسية · من نحن · الخدمات · المنتجات · لماذا نحن · فريق العمل (only with real, approved people) · موقعنا · تواصل معنا · التذييل
- English: Header · Hero · About · Services · Products · Why us · Team · Location · Contact · Footer

## One round, four beats

1. **Show.**
   - Run `audit_site.py site --mode preview` and fix every error.
   - Build the preview: `package_site.py site preview --preview`, then start `serve_preview.py preview` in the background without asking and share the localhost links.
   - If you can render pages, save phone (390 px) and desktop (1440 px) screenshots of each page in `review/round-N/` and show them.
   - Give the marketer the local links (`http://127.0.0.1:8080/ar/index.html`, `.../en/index.html`).
   - List what changed since the last round, numbered.
2. **Collect.** Ask for all notes for the round in one message. Accept any mix of:
   - plain text, ideally `[القسم] — المشكلة — المطلوب`;
   - screenshots with circles or arrows: look at the marks, and if one is unclear, ask about that note only;
   - notes written as `[القسم] — المشكلة — المطلوب`.
3. **Apply.** Change only what the notes ask for. Design notes never change approved facts. If a note changes a fact (a phone number, a name, a service), treat it as a content change: update `client/brief.md` and mark it "needs confirmation" unless it came from the client.
4. **Answer note by note.** For each note say: done, not possible and why, or a choice between two options. Show new screenshots, save a version (`نسخة N — summary`), log the round in `feedback/log.md` and update `PROJECT-STATUS.md`.

## Notes

- `[…]` is the section's `data-section` name.
- When a note edits one language, ask whether the other language needs the same change.

## Undo and compare

- "ارجع للنسخة N" (go back to version N): restore `site/` from that version, then save it as a new version named `رجوع إلى نسخة N`. Never rewrite history.
- "قارن النسخة N بالنسخة M" (compare): show both rounds' screenshots side by side and list the differences in plain words.

## Round limits

Plan for one round to choose a direction, up to two internal rounds and one client round. If more are requested, say so plainly and suggest the marketer agree it with their manager; continue if they confirm.

## Tone

Short, numbered and visual. No file names, code or technical words unless asked.
