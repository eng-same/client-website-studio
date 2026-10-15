# Handover

Speak the marketer's language. Avoid words like "artifact", "webroot", "deploy", "build", "responsive", "metadata" and "JavaScript" unless they ask.

## What to tell the marketer

"The company website is ready for review. It includes: [the approved sections]. You can view it in Arabic and English. Here is the preview: [link, only if it is real]."

"Before it goes live, please confirm with the client: the company name, the service descriptions, the address, the phone numbers and the company email."

"When everything is approved, use the website ZIP in the handover folder and the publishing steps from your training. The client's account owner should be present for the final handover."

"Checks completed: [only checks actually performed]. Still to check: [anything not verified]."

## Files in `handover/`

- The release ZIP and its `.json` record (file list, checksum, audit result, approval note).
- `quality-report.md`: what was tested, when, by whom, and what remains unverified.
- `handover-record.md`: the internal record below.

## Internal handover record

Client · domain · hosting account owner · business mailbox(es) · approval (who, date, channel) · live URL · publish date · backup location · domain renewal date · hosting renewal date · who renews · reviewer · outstanding issues.

Never include passwords, access tokens or personal identity documents.

## Close the project

- Set `PROJECT-STATUS.md` to the final stage, with the live URL and renewal dates.
- Save a final version named `تسليم`.
- Remind the marketer to delete the client's preview folder from the agency's hosting.
- Remind them that if the domain lapses, the website and the company email stop together.
