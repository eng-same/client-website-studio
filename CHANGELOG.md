# Changelog

Marketers always download the `main` branch. Existing client projects keep the version they started with until someone asks the agent to «حدّث العدّة».

## 2.1.0 — 2026-10-16

- **Review Mode removed.** Previews no longer carry a toolbar; feedback is given as plain notes or screenshots. `--label` is gone.
- **Local preview by default.** New `serve_preview.py`; the agent always serves the preview on localhost without asking for approval.
- **check_layout.py:** measures sideways overflow of every page at six widths in headless Edge/Chrome.
- Design rules: required rich footer with contact icons, polished buttons, and a distinctive language switch.

## 2.0.0 — 2026-10-15

- **One-paste start.** `START.md` sets up each client folder from the `main` branch: installs the skill for Claude (`.claude/skills`) and for Codex, Antigravity and other agents (`.agents/skills`), creates the folder layout, and makes the first local save point. Returning projects resume from `PROJECT-STATUS.md`.
- **Client folder template.** `PROJECT-STATUS.md` (status in plain Arabic), `START-HERE.md` (ready-made prompts for marketers), `AGENTS.md` and `CLAUDE.md`.
- **Clear ownership.** The marketing team owns intake, brand identity, logo and client communication. The skill organises their material and never designs logos or identities.
- **Brief template** with a source and status for every fact, a check against registration documents, and a fact sheet the client approves before release.
- **Review rounds.** Fixed section names, one batch of notes per round, note-by-note answers, saved versions with undo and compare, and round limits.
- **Review Mode.** A preview-only toolbar: click any part of the page to leave a note, or edit text in place, then copy the notes or send them on WhatsApp. It is injected into previews only and blocked from the live site.
- **Client previews** on the agency's own hosting, protected per client with cPanel Directory Privacy.
- **audit_site.py:** preview and release modes; `[[NEEDS]]` markers; Central Bank claim detection in Arabic and English; CSS `url()` and `srcset` checks; errors for paths starting with `/`; phone, WhatsApp and email link checks; language switch check; duplicate ids; `data-section` names; readable summary; safe Arabic output on Windows.
- **package_site.py:** runs the audit first; a release needs `--approval` and writes a `.json` record with a checksum; reproducible ZIPs; `--preview` builds a folder or ZIP with Review Mode and a noindex tag without touching `site/`.
- Tests and a GitHub Actions workflow.

## 1.x

- First version of the skill: conversation workflow, design, implementation, localisation, quality and publishing references, plus the first audit and packaging scripts.
