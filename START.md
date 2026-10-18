# Studio start-up: instructions for the AI agent

You are setting up or resuming a client website project for a marketer who does not read code. These steps run for the client's project folder (the folder your session was opened in).

Talk to the marketer in Arabic, in plain words, one question at a time. Never show code, commands or file contents unless they ask. Never ask for a password. Never ask the marketer to run a command, choose a tool, rename a folder or move files.

## The one rule: the skill never goes into the client's project

The kit (this repository, including this file, `skills/`, `workspace-template/`, `tests/`) is instructions for you. It must never be cloned, downloaded, unzipped or copied into the client's project folder or any subfolder of it, and the marketer must never see it there.

- Do not create `.studio-kit/`, `.claude/skills/client-website-studio/`, `.agents/skills/client-website-studio/` or any other copy of the skill inside the project.
- Install it once per computer, in your agent's own **user-level** skills folder (step 2).
- If you need to download the kit, use a temporary or kit folder **outside** every client project (step 2).

## 1. New, returning or existing project?

Look at the project folder first, without changing anything.

- **`PROJECT-STATUS.md` exists:** returning project.
  - Do not copy anything over existing files, and do not update the skill unless the marketer asks ("حدّث العدّة").
  - Read `PROJECT-STATUS.md`, `client/brief.md` and `feedback/log.md`. Tell the marketer in three short lines where the project stands and what comes next. Then wait.
  - Run `python3 <skill>/scripts/audit_site.py . --mode preview` once. If it reports a wrapper folder (for example `site/`) or skill files inside the project, run `python3 <skill>/scripts/normalize_project.py .` to see the plan, then with `--apply` (it makes a full backup outside the project first, and never overwrites anything). Tell the marketer in one plain sentence what you tidied.
- **No `PROJECT-STATUS.md`, but the folder already has website files** (an `index.html`, `ar/`, `en/`, `site/` or similar): an existing project from before the studio. Do not start over and do not create a second site inside it. Identify the real project root, run the audit and `normalize_project.py` as above, keep every business file and design decision, then continue with step 3 (without overwriting anything).
- **Empty folder or only the marketer's material:** new project. Continue with step 2.

## 2. Install the skill outside the project

First check whether `client-website-studio` is already installed at user level and is current (its `SKILL.md` `metadata.version` equals the `VERSION` in the kit). If so, skip to step 3.

Otherwise get the kit **outside the project**:

1. Choose a kit folder that is not inside any client project, for example `~/.client-website-studio/kit` (Windows: `%USERPROFILE%\.client-website-studio\kit`). If it exists, update it (`git -C <kit> pull`); if not, `git clone --depth 1 --branch main https://github.com/eng-same/client-website-studio.git <kit>`. If git is unavailable, download `https://github.com/eng-same/client-website-studio/archive/refs/heads/main.zip` and unpack it into that kit folder.
2. Copy only `<kit>/skills/client-website-studio/` into the user-level skills folder your agent documents:

   | Agent | User-level skills folder |
   | --- | --- |
   | Claude Code | `~/.claude/skills/client-website-studio/` |
   | Codex and other agents that follow the `.agents` convention | `~/.agents/skills/client-website-studio/` |

   Install into the folder for the agent you are, plus the other one if it is harmless to create. If your own agent documents a different user-level location, use that instead. Check your tool's current documentation if unsure.
3. Open and read the installed `SKILL.md` yourself now, even if your tool also loads skills automatically. `<skill>` below means that installed folder. Follow it from here on.

If you cannot write to a user-level folder, keep the kit folder from step 1 and use its `skills/client-website-studio/` as `<skill>`. Still never put it in the project.

## 3. Build the project folder

The project folder **is the website**: `index.html`, `ar/`, `en/` and `assets/` sit directly in it. There is no `site/` wrapper folder. Working folders live beside the website files and are never shipped.

1. Copy every file from `<kit>/workspace-template/` into the project folder without overwriting anything that already exists.
2. Create these folders if missing: `client/inbox`, `client/documents`, `client/approvals`, `brand`, `concepts`, `review`, `feedback`, `handover`.
3. Copy `<skill>/assets/brief-template.md` to `client/brief.md` if it does not exist.
4. Create `feedback/log.md` with the heading `# سجل الملاحظات` if it does not exist.
5. In `PROJECT-STATUS.md`, fill in the client name from the marketer's message, today's date, and the kit version from the kit's `VERSION`.

## 4. First save point

If git is available:

1. `git init` (skip if `.git` already exists).
2. Add these lines to `.git/info/exclude`: `preview/`, `*.zip`, `__pycache__/`.
3. If git has no user name or email configured, set them for this folder only: `git config user.name "Studio"` and `git config user.email "studio@localhost"`.
4. Commit everything with the message `بداية المشروع`.

Never add a remote and never push. Client files must never leave this computer through git. If git is not available, skip this step; the skill keeps numbered copies instead.

## 5. Hand over to the marketer

- If `client/inbox/` already has files, say so and start the skill's **Brief** stage straight away.
- Otherwise, tell the marketer in two or three short sentences that the folder is ready, and that they should put everything they have from the client (notes, form answers, WhatsApp screenshots, logo, photos, documents) into the folder `client/inbox`, then write "جاهز".

## Updating the kit ("حدّث العدّة")

Only when the marketer asks:

1. Update the kit folder outside the project (`git -C <kit> pull`, or download the `main` ZIP again).
2. Replace the user-level skill copy from `<kit>/skills/client-website-studio/`.
3. Do not touch the website files, `client/` or any other project file.
4. Record the new kit version in `PROJECT-STATUS.md`, and tell the marketer in one line what changed according to the kit's `CHANGELOG.md`.
