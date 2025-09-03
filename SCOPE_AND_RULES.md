Scope and Rules for Bulletin Builder
====================================

Purpose
-------
The Bulletin Builder exists to let a single editor (the repo owner) produce a reliable, email-ready bulletin that can be pasted into FrontSteps and delivered to common email clients (Outlook, Gmail, etc.).

Core features (must be preserved and tested)
-------------------------------------------
1. Import: CSV/JSON events and announcements should be importable and normalized.
2. Edit: Add, remove, reorder modular sections (announcements, events, images, custom text).
3. Preview: Render a WYSIWYG preview and allow opening the result in a browser.
4. Export: Produce email-ready HTML and plaintext; postprocess must strip head/doctype/scripts and inline CSS.
5. PDF: Export to PDF using WeasyPrint for print distribution.

Out of scope (no random features)
---------------------------------
- No AI features beyond minimal, opt-in helpers.
- No automatic auto-update integration unless explicitly requested and tested.
- No deep third-party integrations (beyond import/export as specified) without prior approval.

Rules (strict)
--------------
1. All changes must reference a ticket/issue. No direct, untracked edits to `main`.
2. All PRs must include tests for any behavior change (unit, integration, or smoke). If a GUI-only tweak cannot be unit-tested, include a headless smoke test where possible.
3. CI must pass before a PR can be merged. Branch protections should be enabled.
4. Any change touching UI, exporter, or postprocess must be reviewed by a CODEOWNER.
5. Keep PRs small and explain the risk and rollback plan.
6. Activity logging must be preserved for export/postprocess actions (for audit).

How to propose a feature (short)
--------------------------------
- Create an issue describing user-visible behavior and acceptance criteria.
- Create a small design note in the PR describing how the change stays within core features.
- Attach tests and screenshots where applicable.

Enforcement
-----------
- `pre-commit` runs format/lint and test pre-push.
- CI runs lint and test; PRs failing CI are blocked.
- CODEOWNERS reviews enforce approvals for critical areas.

