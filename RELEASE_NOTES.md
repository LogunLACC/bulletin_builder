# Release notes — release/final-merge

Date: 2025-09-03

This release focuses on hardening the GUI and persistence for the Bulletin Builder.

Key fixes
- Fixed duplicate <h2> headers in templates (image & announcements partials).
- Restored File and Tools menu entries and provided safe menu handlers for headless and GUI modes.
- Added importer handlers and menu wiring for announcements and events import flows.
- Fixed announcements editor persistence: programmatic and GUI edits now persist to `user_drafts/*.json`.
- Adjusted Events grid CTA sizing.
- Fixed runtime error in Custom Text editor.

Validation
- Added `tests/test_announcements_persistence.py` to assert announcements are saved to JSON.
- Ran smoke script `tools/smoke_announcements_gui.py` and saved `user_drafts/smoke_draft.json`.

Next steps
- Consider adding more UI integration tests and manual QA for menu flows.
# Release notes – 0.1.1

Date: 2025-09-09

Highlights
- Outlook-safe email buttons: Converted CTA anchors to bulletproof VML buttons in templates; parameterized button color from `settings.colors.primary`.
- Inline safety postprocess: Enforces `margin:0; padding:0` on `<a>/<img>`, and `border-collapse/border-spacing` on `<table>` with `border:none` for `<td>` (idempotent).
- Announcements editor UX: Added Remove/Up/Down controls and support for link + link title fields.
- Settings view redesign: Centered layout, better spacing, fills the pane; added Auto‑import Events toggle; Events Window selector.
- Window behavior: Remembers geometry/state; starts maximized without flicker; dialogs center over parent and open on same screen.
- Auto‑sync control: “Run Auto Sync” now runs regardless of the toggle; automatic sync still respects the toggle on startup.

Quality
- Added tests for VML button rendering, theme color pass‑through, inline safety, and postprocess idempotency.
- All tests passing locally.

Notes
- PyInstaller specs included (`bulletin_builder.spec`, `packaging/bulletin_builder.spec`). Use `scripts/build_exe.py` for a clean build.

# Release notes �?" release/final-merge
