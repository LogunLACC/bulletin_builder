Core purpose
-----------
This application exists to create community email bulletins quickly and safely.

Primary goals (high priority):
- Build and export an email-ready bulletin (HTML + plaintext) from modular sections.
- Import events/announcements from CSV/JSON feeds and render them as bulletin sections.
- Offer an editor to reorder/add/remove sections and preview the generated HTML.
- Export to PDF (via WeasyPrint) for print distributions.

Non-core / deferred (do not implement without explicit approval):
- AI-driven subject suggestion beyond a simple helper
- Auto-update and packaging automation beyond release scripts
- Deep integrations (Google AI) unless covered with tests and opt-in config

Stability rules
--------------
- All UI changes must include regression tests that exercise non-GUI behavior when possible.
- CI must pass before merging to `main`.
- UX-only cosmetic changes that do not affect data paths can be merged after review, but larger changes require a feature branch and PR.
