## Summary
Describe the change and why it's needed. Keep PRs small and focused on a single user-visible change.

## Related issues
Link an issue or ticket that motivates this change. If this is a maintenance or bugfix change, reference the existing issue or create one and link it here. PRs without an issue will be rejected unless pre-approved by a CODEOWNER.

## Scope & Core Alignment (required)
- Which core feature does this change affect? (see `CORE_FEATURES.md`)
- Confirm this change is IN-SCOPE for v1 core features: (yes/no) — PRs marked "no" must include explicit approval from a code owner.

## Checklist (required)
- [ ] Tests added/updated for any change in behavior (unit or smoke)
- [ ] Pre-commit hooks run locally and are clean
- [ ] All tests pass locally and CI green
- [ ] Includes a short risk summary and rollout plan (if applicable)
- [ ] Assigned reviewer from `CODEOWNERS` or explicit approval

## Scope freeze
Only changes within the agreed core features are allowed on the `main` branch; large refactors, UI redesigns, or surface changes must be implemented on a feature branch and include tests and a short design note.
