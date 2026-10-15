# Review rounds: feedback without code

Marketers judge what they see and never open code. Every round ends with something they can look at and a saved version they can return to.

## Section names

Each top-level `<header>`, `<section>` and `<footer>` carries a `data-section` name in the page's language. Use the same names in chat, in the status file and in screenshots.

- Arabic: الشريط العلوي · الواجهة الرئيسية · من نحن · الخدمات · المنتجات · لماذا نحن · فريق العمل (only with real, approved people) · موقعنا · تواصل معنا · التذييل
- English: Header · Hero · About · Services · Products · Why us · Team · Location · Contact · Footer

## One round, four beats

1. **Show.**
   - Run `audit_site.py site --mode preview` and fix every error.
   - Build the preview: `package_site.py site preview --preview --label "نسخة N"`.
   - If you can render pages, save phone (390 px) and desktop (1440 px) screenshots of each page in `review/round-N/` and show them.
   - Tell the marketer they can open the preview themselves by double-clicking `preview/ar/index.html`, and use the Review Mode buttons at the bottom of the page.
   - List what changed since the last round, numbered.
2. **Collect.** Ask for all notes for the round in one message. Accept any mix of:
   - plain text, ideally `[القسم] — المشكلة — المطلوب`;
   - screenshots with circles or arrows: look at the marks, and if one is unclear, ask about that note only;
   - a Review Mode list (format below).
3. **Apply.** Change only what the notes ask for. Design notes never change approved facts. If a note changes a fact (a phone number, a name, a service), treat it as a content change: update `client/brief.md` and mark it "needs confirmation" unless it came from the client.
4. **Answer note by note.** For each note say: done, not possible and why, or a choice between two options. Show new screenshots, save a version (`نسخة N — summary`), log the round in `feedback/log.md` and update `PROJECT-STATUS.md`.

## Review Mode lists

Previews include a small toolbar at the bottom of each page. Anyone can click a part of the page to leave a note, or switch on text editing and type directly on the page. "نسخ الملاحظات" (Copy notes) produces a list like this:

```text
ملاحظات المعاينة — شركة النور — نسخة 4
الصفحة: ar/index.html
1. [الواجهة الرئيسية] تعديل نص: «نخدمكم منذ 2010» ← «نخدم بنغازي منذ 2010» (هاتف)
2. [الخدمات] عند «النقل البري»: الصورة غير واضحة، نريد صورة المستودع (كمبيوتر)
```

- `[…]` is the section's `data-section` name; "عند «…»" quotes the element the note was attached to.
- Text edits give the exact old and new wording. Apply them to the matching page, then ask whether the other language needs the same change.
- The word in brackets at the end says whether the reviewer was on a phone or a computer.
- Review Mode exists only in `preview/` and in preview ZIPs. Never copy it into `site/`; the audit fails if you do.

## Undo and compare

- "ارجع للنسخة N" (go back to version N): restore `site/` from that version, then save it as a new version named `رجوع إلى نسخة N`. Never rewrite history.
- "قارن النسخة N بالنسخة M" (compare): show both rounds' screenshots side by side and list the differences in plain words.

## Round limits

Plan for one round to choose a direction, up to two internal rounds and one client round. If more are requested, say so plainly and suggest the marketer agree it with their manager; continue if they confirm.

## Tone

Short, numbered and visual. No file names, code or technical words unless asked.
