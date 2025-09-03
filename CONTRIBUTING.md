This repository uses a light-weight CI and pre-commit checks to keep changes stable.

Local pre-checks
- Install pre-commit hooks:

```powershell
python -m pip install --upgrade pip
pip install pre-commit
pre-commit install
pre-commit run --all-files
```

Run tests locally

```powershell
python -m pip install -r requirements.txt
pytest -q
```

When opening a PR:
- Ensure tests pass locally and pre-commit hooks are clean.
- Describe any UI changes and include a screenshot for GUI fixes.
