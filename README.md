# Client Website Studio

A kit for marketing teams who build bilingual Arabic/English company websites with an AI agent and publish them on client-owned Libyan Spider hosting (Plesk/IIS or cPanel). Marketers never touch code: they paste one prompt, drop the client's material into a folder, and give feedback on what they see.

## Who does what

| Who | Responsible for |
| --- | --- |
| Marketing team | Client relationship, intake, brand identity and logo, photos, content approval, all client communication |
| AI agent with this skill | Organising the team's material, building the site, review rounds, previews, the verified `DEPLOY-READY.zip`, step-by-step publishing guidance |
| Client | Domain, hosting, mailboxes, renewals and every password |

## Start a new client

1. Create an empty folder named after the client, in Latin letters with no spaces, for example `clients/al-noor-trading`.
2. Open that folder in your AI agent (Claude Code, Codex, Antigravity, or another agent that supports Agent Skills).
3. Paste this prompt and replace the company name:

```text
مشروع موقع جديد للعميل: [اسم الشركة]

١. حمّل عدّة الاستوديو إلى مكان خارج هذا المجلد (وليس داخله)، وثبّت المهارة client-website-studio في مجلد المهارات الخاص بالمستخدم حسب أداتك:
https://github.com/eng-same/client-website-studio
ثم اقرأ START.md من العدّة ونفّذ ما فيه بالترتيب.
لا تنسخ العدّة ولا المهارة إلى هذا المجلد أبداً.

٢. ملفات الموقع تكون مباشرة في هذا المجلد، وملف index.html في جذره.

٣. كلّمني بالعربية وبكلمات بسيطة، سؤالاً واحداً في كل مرة.
لا تطلب مني أي كلمة مرور، ولا تنشر أي شيء دون موافقتي الصريحة.
```

The same prompt in English:

```text
New website project for client: [Company name]

1. Get the studio kit OUTSIDE this folder and install the client-website-studio skill in your
agent's user-level skills folder: https://github.com/eng-same/client-website-studio
Then read START.md from the kit and follow it in order. Never copy the kit or the skill into this folder.

2. The website files sit directly in this folder, with index.html at its root.

3. Talk to me in plain words, one question at a time.
Never ask me for a password, and never publish anything without my explicit approval.
```

The skill is installed once per computer (Claude Code: `~/.claude/skills/`, Codex and other `.agents`-convention agents: `~/.agents/skills/`). The client folder only ever holds the client's website and private working folders, never the kit. The agent creates the layout and asks the marketer to drop the client's material into `client/inbox`.

**Existing project?** Open the project folder and paste the same prompt. If an earlier version put the website in a `site/` folder, or copied the kit into the project, the agent runs `normalize_project.py`: it shows the plan, makes a full backup outside the project, moves the website up to the root and removes the copied kit, without overwriting anything.

## What the marketer ends up with

One file: `handover/DEPLOY-READY.zip`. It contains only the self-contained `index.html` directly at its root, so it is extracted straight into `httpdocs` (Plesk) or `public_html` (cPanel) and works with nothing moved afterwards. It is built by `package_site.py`, which audits the site, builds the ZIP from the website files only, then re-opens it, extracts it, audits the extract and serves it over HTTP, and deletes it if anything fails.

## Day-to-day use

Every client folder contains `START-HERE.md` in Arabic with ready-made prompts. The main ones:

| When | Prompt |
| --- | --- |
| Coming back to a project | كمّل المشروع. اقرأ PROJECT-STATUS.md أولاً وقل لي أين وصلنا وما الخطوة التالية. |
| New files from the client | وضعت ملفات جديدة في client/inbox، حدّث البيانات وقل لي ما الذي ينقص. |
| Feedback on the design | Written notes or a marked-up screenshot |
| Going back | ارجع للنسخة 3. |
| Client preview | جهّز ملف المعاينة للعميل. |
| Publishing | العميل وافق (من، متى، وكيف). جهّز الموقع للنشر وأرشدني خطوة بخطوة. |

**Local preview.** After every build the agent starts the preview on your own computer (`http://127.0.0.1:8080`) without asking, so you can open it straight away. It is only reachable from your computer.

**Starting a new client?** Copy the ready-made prompt from [STARTING-PROMPT.md](STARTING-PROMPT.md) and fill in the client's answers.

## What is in this repo

```text
START.md                       set-up and resume instructions the agent follows
VERSION, CHANGELOG.md
skills/client-website-studio/  the Agent Skill (installed outside client projects)
  SKILL.md
  references/                  intake, design, build, languages, review rounds, quality, publishing, handover
  assets/                      brief template
  scripts/                     audit_site.py, package_site.py, verify_zip.py, normalize_project.py,
                               check_live.py, serve_preview.py, check_layout.py (Python standard library only)
workspace-template/            files copied into every new client folder
tests/                         sample site and script tests
```

## Scripts (for the engineer)

Run from the client's project folder (the website files sit directly in it):

```text
python3 <skill>/scripts/audit_site.py . --mode preview
python3 <skill>/scripts/audit_site.py .
python3 <skill>/scripts/normalize_project.py . [--apply]
python3 <skill>/scripts/package_site.py . --list
python3 <skill>/scripts/package_site.py . preview --preview
python3 <skill>/scripts/package_site.py . --approval "who, when, how"      # handover/DEPLOY-READY.zip
python3 <skill>/scripts/verify_zip.py handover/DEPLOY-READY.zip
python3 <skill>/scripts/check_live.py https://example.ly/ --zip handover/DEPLOY-READY.zip
python3 tests/test_scripts.py                                              # from this repo
```

The audit reads source files only. It does not prove mobile layout, accessibility, translation quality, live behaviour, regulatory compliance or successful publishing; those need a browser check, `check_live.py` and human review. A correct ZIP also does not repair an existing broken IIS/ASP.NET configuration on the host; see `references/publishing.md`.

## Releasing a new version

1. Work on `main` and run `python3 tests/test_scripts.py`.
2. Try the change on one sample or real client.
3. Update `VERSION`, the `version` in `SKILL.md` and `CHANGELOG.md`.

Marketers always get `main`. Existing projects keep their version until someone asks the agent «حدّث العدّة». Every marketer's agent follows `START.md` from `main`, so protect that branch and keep two-factor authentication on the account.

## Rules for this public repo

Never commit client material, client websites, passwords, hosting details or anything from a client folder. Client folders stay on the team's computers.

## Bank requirements

These websites give a company a professional presence, its own domain and a business mailbox. Nothing in this kit verifies Central Bank of Libya or any bank's requirements, and the audit blocks pages that claim compliance. Ask the client for their bank's current written checklist.

## Optional design skills

Install separately if wanted; this skill's plain HTML/CSS/JS rules take priority over their defaults.

- https://github.com/nextlevelbuilder/ui-ux-pro-max-skill
- https://github.com/anthropics/claude-code/tree/main/plugins/frontend-design
- https://github.com/vercel-labs/agent-skills/tree/main/skills/web-design-guidelines

## Arabic-first, one-file delivery (v4)

العربية هي الأساس: الموقع يفتح بالعربي واتجاهه من اليمين لليسار، والإنجليزية موجودة كاملة في نفس الملف. الصور والخطوط والتنسيقات والحركات كلها داخل `index.html`؛ لا توجد صفحات أو ملفات إضافية لرفعها.

المساعد يختار عبارات البحث العربية المناسبة من اسم العميل وخدماته وموقعه المؤكد، ويكتب عنوان الصفحة ووصفها وبيانات الشركة تلقائياً. لا يحتاج الموظف لمعرفة إعدادات البحث، ولا يخترع المساعد نشاط الشركة من اسمها أو يضمن ترتيباً في جوجل.

Existing projects: back up before migrating. `normalize_project.py` only fixes folder placement; it does not combine legacy language pages or embed their assets. The agent must preserve approved content/design, move originals into private working folders, then consolidate and audit `index.html`. Older multi-file outputs are now rejected even in preview. A missing optional canonical URL remains documented as pending until the real domain is confirmed.
