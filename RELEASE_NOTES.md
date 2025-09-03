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
