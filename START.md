# Studio start-up: instructions for the AI agent

You are setting up or resuming a client website project for a marketer who does not read code. These steps run inside the client's project folder, where the kit has been downloaded to `.studio-kit/`.

Talk to the marketer in Arabic, in plain words, one question at a time. Never show code, commands or file contents unless they ask. Never ask for a password.

## 1. New or returning project?

- **`PROJECT-STATUS.md` exists:** this is a returning project.
  - Do not copy anything over existing files, and do not update the skill unless the marketer asks for it ("حدّث العدّة").
  - Read `PROJECT-STATUS.md`, `client/brief.md` and `feedback/log.md`.
  - Tell the marketer in three short lines where the project stands and what comes next. Then wait.
- **No `PROJECT-STATUS.md`:** this is a new project. Continue with step 2.

## 2. Install the skill

Copy `.studio-kit/skills/client-website-studio/` into both of these folders, creating them if needed:

- `.claude/skills/client-website-studio/`
- `.agents/skills/client-website-studio/`

Then open and read `.claude/skills/client-website-studio/SKILL.md` yourself now, even if your tool also loads skills automatically. Follow it from here on.

## 3. Build the client folder

1. Copy every file from `.studio-kit/workspace-template/` into this folder without overwriting anything that already exists.
2. Create these folders if missing: `client/inbox`, `client/documents`, `client/approvals`, `brand`, `concepts`, `site`, `review`, `feedback`, `handover`.
3. Copy `.studio-kit/skills/client-website-studio/assets/brief-template.md` to `client/brief.md` if it does not exist.
4. Create `feedback/log.md` with the heading `# سجل الملاحظات` if it does not exist.
5. In `PROJECT-STATUS.md`, fill in the client name from the marketer's message, today's date, and the kit version from `.studio-kit/VERSION`.

## 4. First save point

If git is available:

1. `git init` (skip if `.git` already exists).
2. Add these lines to `.git/info/exclude`: `.studio-kit/`, `preview/`, `*.zip`, `__pycache__/`.
3. If git has no user name or email configured, set them for this folder only: `git config user.name "Studio"` and `git config user.email "studio@localhost"`.
4. Commit everything with the message `بداية المشروع`.

Never add a remote and never push. Client files must never leave this computer through git. If git is not available, skip this step; the skill keeps numbered copies instead.

## 5. Hand over to the marketer

- If `client/inbox/` already has files, say so and start the skill's **Brief** stage straight away.
- Otherwise, tell the marketer in two or three short sentences that the folder is ready, and that they should put everything they have from the client (notes, form answers, WhatsApp screenshots, logo, photos, documents) into the folder `client/inbox`, then write "جاهز".

## Updating the kit ("حدّث العدّة")

Only when the marketer asks:

1. Update `.studio-kit/` (`git -C .studio-kit pull`, or download the `main` ZIP again).
2. Replace both skill copies from `.studio-kit/skills/client-website-studio/`.
3. Do not touch `site/`, `client/` or any other project file.
4. Record the new kit version in `PROJECT-STATUS.md`, and tell the marketer in one line what changed according to `.studio-kit/CHANGELOG.md`.
