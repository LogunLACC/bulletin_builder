# LACC Bulletin Builder — Baseline Resync Checklist
- Sanitizer runs **email-only**
- Web/builder keeps `<!DOCTYPE>` + `<head>` (Premailer/transform not applied)
- URL upgrader runs in both; AVIF→JPG happens **email-only**
- Run audits for both profiles before merge
# LACC Bulletin Builder — Baseline Resync Checklist

This is a **no-NPM** baseline plan to get everything back to a clean, predictable state.

## 0) Create a safe baseline branch
```bash
git checkout main && git pull
git checkout -b baseline/resync-$(date +%Y-%m-%d)
```

## 1) Confirm sanitizer scope
- **Email-only**: `sanitize_email_html()` **must** be invoked *only* in the email workflow.
- **Web/builder** retains `<!DOCTYPE>`, `<head>`, styles, and scripts.
- Keep the URL upgrader in both paths; AVIF→JPG fallback only in **email** path.

## 2) Add the audit tool
Copy `tools/baseline_audit.py` into your repo (this command does it).

### Run audits on your outputs
```bash
# Example:
python tools/baseline_audit.py --mode web   path/to/builder.html
python tools/baseline_audit.py --mode email path/to/email.html
```

**Pass criteria**
- **Web**: has `<!doctype>` and `<head>`; no `http://` mixed content; no empty `.event-card__title` tags.
- **Email**: no `<!doctype>/<head>/<script>/<link rel=stylesheet>`; no inline `on*=`; no `http://`; no `.avif`; and style rules:
  - `<a>` and `<img>` styles start with `margin:0; padding:0;`
  - `<table>` includes `border-collapse:collapse;`
  - `<td>` styles start with `border:none;`

## 3) Tests that lock behavior
- Scope tests (builder keeps head/doctype; email strips them)
- Style enforcement tests for `<a>/<img>/<table>/<td>`
- Mixed-content tests (no `http://` in outputs)
- Email-only AVIF test (ban or rewrite)

## 4) HTTPS & secure-context
- Silent redirect in prod only; never alert.
- Guard SW/clipboard behind `isSecureContext || localhost`.
- Keep URL upgrader active to avoid mixed content in web.

## 5) Green checklist before merging
- ✅ All audits pass (web + email samples)
- ✅ Pytests green
- ✅ Manual spot-check in a real email client (Gmail/Outlook web)
- ✅ Manual spot-check in the target web host (HTTPS page)
