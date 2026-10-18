# Previews and publishing on Libyan Spider (Plesk/IIS and cPanel)

Explain every step in plain words, **one screen at a time**, and wait until the marketer says they see the named button before giving the next step. Never collect passwords in chat or in the project folder. Control-panel labels differ between versions and plans; describe what to look for and ask for a screenshot if unsure.

**Which panel?** Ask the marketer to send a screenshot of the client's hosting control panel. Plesk (Windows/IIS, website folder `httpdocs`) and cPanel (website folder usually `public_html`) are both used by Libyan Spider; other plans may differ. Use the matching section below. Four different things can be wrong, and a correct ZIP fixes only the first: (1) the website file structure, (2) the ZIP, (3) the host's default-document setting, (4) an existing server-side configuration. Keep them apart when you explain.

## Client preview (on the agency's own hosting)

The agency keeps one preview area on its own hosting, for example `preview.<agency-domain>`, with one folder per client.

1. Build the preview ZIP: `package_site.py . handover/preview-CLIENT.zip --preview`. It adds a no-index tag to the copy; the project files stay untouched.
2. Agency cPanel → **File Manager** → the preview area → create a folder named after the client → open it → **Upload** the ZIP → right-click it → **Extract** → delete the ZIP.
3. cPanel → **Directory Privacy** → open the client's folder → tick "Password protect this directory" → **Save** → add a user name and password. Each client gets its own password, and subfolders inherit the protection ([cPanel docs](https://docs.cpanel.net/cpanel/files/directory-privacy/)).
4. The marketer sends the link and the password to the client in two separate messages.
5. Delete the client's preview folder once the real site is live.

The preview works inside a subfolder only because every path in the site is relative; the audit enforces this.

## Before publishing to the client's account

1. The client has an active hosting plan and domain in **their own** Libyan Spider account, with the correct spelling, and the client is responsible for renewals. The client keeps their own login and recovery access.
2. The client's content approval is recorded in `PROJECT-STATUS.md`, with a screenshot in `client/approvals/`.
3. Confirm which folder is this domain's website folder. For the main domain it is usually `public_html`; an add-on domain can use a different folder. Do not assume; check in cPanel's **Domains** page or ask the host.
4. If a website already exists, take a backup and get explicit approval before replacing anything. Agree how to roll back.
5. Build the release ZIP: `package_site.py . --approval "…"`. It writes `handover/DEPLOY-READY.zip` from the website files only, refuses to build if the release audit fails, puts `index.html` at the ZIP's root, and checks the finished ZIP (extract, audit, serve over HTTP) before it keeps it. This is the only file to publish.

## Publishing steps for the marketer: Plesk on Windows/IIS

Use when the client's panel is Plesk. The ZIP is extracted **directly into `httpdocs`**; nothing is moved afterwards.

1. Sign in to Plesk → **Websites & Domains** → the client's domain → **File Manager**. Open `httpdocs` (not another folder).
2. **Backup first.** If the domain already has files (for example `index.php`, `web.config`, an old `site/` folder or a default page), select them → **Compress** (or **Download**) and keep that copy. Do not delete anything yet, and ask for explicit approval before replacing a live site.
3. **Upload** `DEPLOY-READY.zip` into `httpdocs` → right-click it → **Extract Files** into `httpdocs` itself (not into a new subfolder) → delete the uploaded ZIP.
4. Check that `index.html`, `en/` and `assets/` (and `ar/` if the site has it) sit **directly inside `httpdocs`**. If they sit inside another folder, the ZIP was extracted into a subfolder; extract it again into `httpdocs` itself and remove the extra folder.
5. **Default document.** Plesk → the domain → **Hosting & DNS** → **IIS Settings** → **Default documents**: `index.html` must be in the list, and Plesk serves the first file it finds from the top of the list. Move `index.html` up or add it. Menu names differ between Plesk versions, and the host may restrict this page; if it is missing, ask Libyan Spider support to put `index.html` first for the domain. (Plesk documents this under IIS Settings; if a default placeholder page still shows although a valid `index.html` exists, the default-document order or an old placeholder file is the usual cause.)
6. **Old files that can break the home page.** An old `index.php`, `Default.aspx` or `index.aspx` can win over `index.html` depending on the order above, and an old `web.config` can turn on ASP.NET and cause "Server Error in '/' Application" or a 403 even though the new files are correct. Do **not** write, overwrite or paste a `web.config` yourself, do not switch off security options and do not turn on detailed error messages. Ask Libyan Spider support to review the existing `web.config` and ASP.NET settings, or, with the client's approval, rename the old file to `web.config.old` and test again; keep it so it can be restored.
7. Security certificate and secure address: Plesk → the domain → **SSL/TLS Certificates** (for example Let's Encrypt), then the domain's **Hosting & DNS** → hosting settings for the permanent SEO-safe 301 redirect from http to https once the certificate is valid. If it will not issue, contact support instead of guessing.
8. **Live check.** Run `check_live.py https://DOMAIN/ --zip handover/DEPLOY-READY.zip` yourself. Say the site is published only when it passes. Typical results: `403` = no default document or unreadable folder (step 5, or ask support to fix folder permissions); `404` for `/en/index.html` = the files are in the wrong folder (step 4); a "Server Error in '/' Application" page = an existing ASP.NET/IIS configuration (step 6). Then ask the marketer to open the domain on a phone and a computer and try the language switch and every contact button.
9. Remove any old nested copy that stayed online (for example `httpdocs/site/`) once the new site works and the backup is safe.
10. Company mailbox: create it through the provider's workflow, then send **and** receive a test message with an outside address. Do not change existing DNS or email records yourself; ask support first.
11. Record the live address, the date and the backup location in the handover record.

## Publishing steps for the marketer: cPanel

1. Sign in to the client's Libyan Spider client area, open cPanel, then **File Manager**.
2. Open the domain's website folder (not the mail folder, not the account's top folder).
3. Back up any existing website files (select them → **Compress** → download the ZIP).
4. **Upload** the release ZIP, right-click it → **Extract**, check that `index.html` sits directly in this folder, then delete the uploaded ZIP.
5. Security certificate: cPanel → **SSL/TLS Status**. The domain and its `www` version should show as covered. If not, press **Run AutoSSL** and check again later; if it still fails, contact Libyan Spider support instead of guessing.
6. Secure address: cPanel → **Domains** → switch on **Force HTTPS Redirect** for the domain, only once the certificate is valid.
7. Visit the domain with `https://` on a phone and a computer. Check the home page, the language switch, logo and images, and every contact button.
8. Company mailbox (for example info@): create it through the provider's workflow, then send **and** receive a test message with an outside address. cPanel's **Email Deliverability** page shows whether the domain's email authentication is set up. Do not change existing DNS or email records yourself; on a domain with email elsewhere, ask support first.
9. Record the live address, the date and the backup location in the handover record.

If publishing fails, restore the backup and contact Libyan Spider support rather than guessing at DNS or email settings.

## Renewals

If the domain or hosting expires, **the website and the company email stop together**. Put renewal dates in the handover record and make sure the client knows who renews and when.

## Sources

- Plesk: [Websites & Domains and default documents (support article)](https://support.plesk.com/hc/en-us/articles/12377015711895-Default-domain-page-is-shown-on-domain-hosted-on-Plesk-server-despite-existence-of-valid-index-file) (menu names vary by Plesk version; confirm on the client's panel)
- Libyan Spider: [File Manager](https://help.libyanspider.com/kb-article/file-mnager-cpanel/), [Upload files to the web root](https://help.libyanspider.com/kb-article/upload-files-from-webroot/), [Create an email account](https://help.libyanspider.com/ar/kb-article/create-an-email-account-in-cpanel-from-the-client-area/)
- cPanel: [Directory Privacy](https://docs.cpanel.net/cpanel/files/directory-privacy/), [Domains](https://docs.cpanel.net/cpanel/domains/domains/), [SSL/TLS Status](https://docs.cpanel.net/cpanel/security/ssl-tls-status/), [Email Deliverability](https://docs.cpanel.net/cpanel/email/email-deliverability-in-cpanel/)

## Bank requirements

If the client mentions bank or Central Bank of Libya requirements, ask them for the current **written** checklist from their bank. Publishing a website does not prove regulatory eligibility, and nothing on the site may claim it does.
