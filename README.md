# Client Website Studio

A kit for marketing teams who build bilingual Arabic/English company websites with an AI agent and publish them on client-owned Libyan Spider cPanel hosting. Marketers never touch code: they paste one prompt, drop the client's material into a folder, and give feedback on what they see.

## Who does what

| Who | Responsible for |
| --- | --- |
| Marketing team | Client relationship, intake, brand identity and logo, photos, content approval, all client communication |
| AI agent with this skill | Organising the team's material, building the site, review rounds, previews, the release ZIP, step-by-step publishing guidance |
| Client | Domain, hosting, mailboxes, renewals and every password |

## Start a new client

1. Create an empty folder named after the client, in Latin letters with no spaces, for example `clients/al-noor-trading`.
2. Open that folder in your AI agent (Claude, Codex, Antigravity, or another agent that supports Agent Skills).
3. Paste this prompt and replace the company name:

```text
مشروع موقع جديد للعميل: [اسم الشركة]

١. حمّل عدّة الاستوديو إلى هذا المجلد بهذا الأمر:
git clone --depth 1 --branch main https://github.com/eng-same/client-website-studio.git .studio-kit
ثم اقرأ الملف .studio-kit/START.md ونفّذ ما فيه بالترتيب.

٢. إن لم ينجح التحميل، توقّف واطلب مني تنزيل هذا الملف ووضعه في هذا المجلد، ثم فكّه أنت باسم .studio-kit وأكمل:
https://github.com/eng-same/client-website-studio/archive/refs/heads/main.zip

٣. كلّمني بالعربية وبكلمات بسيطة، سؤالاً واحداً في كل مرة.
لا تطلب مني أي كلمة مرور، ولا تنشر أي شيء دون موافقتي الصريحة.
```

The same prompt in English:

```text
New website project for client: [Company name]

1. Get the studio kit into this folder:
git clone --depth 1 --branch main https://github.com/eng-same/client-website-studio.git .studio-kit
Then read .studio-kit/START.md and follow it in order.

2. If the download fails, stop and ask me to download this file into this folder,
then unpack it yourself as .studio-kit and continue:
https://github.com/eng-same/client-website-studio/archive/refs/heads/main.zip

3. Talk to me in plain words, one question at a time.
Never ask me for a password, and never publish anything without my explicit approval.
```

The agent installs the skill into the client folder, creates the folder layout, and asks the marketer to drop the client's material into `client/inbox`.

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
skills/client-website-studio/  the Agent Skill
  SKILL.md
  references/                  intake, design, build, languages, review rounds, quality, publishing, handover
  assets/                      brief template
  scripts/                     audit_site.py, package_site.py (Python standard library only)
workspace-template/            files copied into every new client folder
tests/                         sample site and script tests
```

## Scripts (for the engineer)

```text
python3 skills/client-website-studio/scripts/audit_site.py path/to/site --mode preview
python3 skills/client-website-studio/scripts/audit_site.py path/to/site
python3 skills/client-website-studio/scripts/package_site.py path/to/site preview --preview
python3 skills/client-website-studio/scripts/package_site.py path/to/site out/domain-20261015.zip --approval "who, when, how"
python3 tests/test_scripts.py
```

The audit reads source files only. It does not prove mobile layout, accessibility, translation quality, live behaviour, regulatory compliance or successful publishing; those need a browser check and human review.

## Releasing a new version

1. Work on `main` and run `python3 tests/test_scripts.py`.
2. Try the change on one sample or real client.
3. Update `VERSION`, the `version` in `SKILL.md` and `CHANGELOG.md`.

Marketers always download `main`. Existing projects keep their version until someone asks the agent «حدّث العدّة». Every marketer's agent follows `START.md` from `main`, so protect that branch and keep two-factor authentication on the account.

## Rules for this public repo

Never commit client material, client websites, passwords, hosting details or anything from a client folder. Client folders stay on the team's computers.

## Bank requirements

These websites give a company a professional presence, its own domain and a business mailbox. Nothing in this kit verifies Central Bank of Libya or any bank's requirements, and the audit blocks pages that claim compliance. Ask the client for their bank's current written checklist.

## Optional design skills

Install separately if wanted; this skill's plain HTML/CSS/JS rules take priority over their defaults.

- https://github.com/nextlevelbuilder/ui-ux-pro-max-skill
- https://github.com/anthropics/claude-code/tree/main/plugins/frontend-design
- https://github.com/vercel-labs/agent-skills/tree/main/skills/web-design-guidelines
