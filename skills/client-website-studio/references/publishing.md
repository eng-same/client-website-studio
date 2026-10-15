# Previews and publishing on Libyan Spider cPanel

Explain every step in plain words, **one screen at a time**, and wait until the marketer says they see the named button before giving the next step. Never collect passwords in chat or in the project folder. cPanel labels can differ slightly between versions; describe what to look for and ask for a screenshot if unsure.

## Client preview (on the agency's own hosting)

The agency keeps one preview area on its own hosting, for example `preview.<agency-domain>`, with one folder per client.

1. Build the preview ZIP: `package_site.py site handover/preview-CLIENT.zip --preview`. It adds a no-index tag to the copy; `site/` stays untouched.
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
5. Build the release ZIP: `package_site.py site handover/DOMAIN-YYYYMMDD.zip --approval "…"`. It refuses to build if the release audit fails, and puts `index.html` at the ZIP's root.

## Publishing steps for the marketer

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

- Libyan Spider: [File Manager](https://help.libyanspider.com/kb-article/file-mnager-cpanel/), [Upload files to the web root](https://help.libyanspider.com/kb-article/upload-files-from-webroot/), [Create an email account](https://help.libyanspider.com/ar/kb-article/create-an-email-account-in-cpanel-from-the-client-area/)
- cPanel: [Directory Privacy](https://docs.cpanel.net/cpanel/files/directory-privacy/), [Domains](https://docs.cpanel.net/cpanel/domains/domains/), [SSL/TLS Status](https://docs.cpanel.net/cpanel/security/ssl-tls-status/), [Email Deliverability](https://docs.cpanel.net/cpanel/email/email-deliverability-in-cpanel/)

## Bank requirements

If the client mentions bank or Central Bank of Libya requirements, ask them for the current **written** checklist from their bank. Publishing a website does not prove regulatory eligibility, and nothing on the site may claim it does.
