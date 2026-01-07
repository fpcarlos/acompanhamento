# GitHub Copilot instructions for this repository 🚀

**Quick context:** I inspected the workspace and found only a Python virtual environment folder (`.venv/`) at the repository root. There are no discoverable application source files or CI configuration files at the time of inspection. This file is intended to help an AI coding agent be immediately productive and explain what to do next when repo content is missing or sparse.

## High-level goals for an AI agent ✅
- Verify repository structure and locate the application code (likely under `src/`, `app/`, `backend/`, or a top-level package).
- If code is missing, create minimal reproducible scaffolding only after confirming the desired framework with maintainers.
- Document any changes as PRs with clear description and tests where applicable.

## What I discovered (explicit, verifiable) 🔍
- Present: `.venv/` (Python virtual environment). This indicates a Python project, but no `requirements.txt`, `pyproject.toml`, `setup.py`, `Pipfile`, or source folders were found.
- Absent: `README.md`, `pyproject.toml`, `requirements.txt`, `tests/`, and any `.github/*` workflow files.

## Priority checks an agent must run first (do these BEFORE writing code) ⚠️
1. Search for application code: PowerShell example:
   - `Get-ChildItem -Recurse -File -Include "*.py","*.ipynb","*.cs","*.js","manage.py"`
2. Check Git history for past structure: `git log --name-only --pretty=format:\"%h %s\" | Select-String -Pattern "src|app|manage.py|requirements" -SimpleMatch`
3. Inspect `.venv` only to detect interpreter version: `Get-Content .venv\pyvenv.cfg | Select-String -Pattern "version|home"`
4. Ask the maintainers (open an issue or comment) if no application code is discovered before making large changes.

## How to run and test locally (Windows PowerShell specifics) 🔧
- Activate venv: `.\.venv\Scripts\Activate.ps1`
- If `requirements.txt` exists: `pip install -r requirements.txt`
- Run tests (if tests use pytest): `python -m pytest -q`
- If `pyproject.toml` / Poetry present: `poetry install` (verify `poetry` in PATH)

> Note: use PowerShell commands above. Do not assume `bash` is available on the developer machine unless CI or docs indicate it.

## Debugging & iterative approach for an agent 🐞
- If a change causes import or environment errors, first re-run `python -c "import sys; print(sys.executable, sys.path)"` inside the activated venv to confirm interpreter.
- When adding scaffold code (e.g., a placeholder `README.md`, `requirements.txt`, or `src/__init__.py`), create a PR with a concise description and a checklist: discovery steps, minimal repro, tests added.

## Project-specific notes (based on current repo state) 💡
- The only reliable signal is a Python `.venv/` — treat this as a Python project but verify the intended framework (Flask, Django, FastAPI, script, etc.) before implementing features.
- Prefer making small, reversible changes and document each step as an issue or PR.

### If you create/encounter a Django project

- Project here now contains a Django project: `projeto_auditoria` with a sample app `auditoria`.
- To get started locally (PowerShell):
   - `.\.venv\Scripts\Activate.ps1`
   - `pip install -r requirements.txt`
   - `python manage.py makemigrations auditoria` (se for a primeira vez)
   - `python manage.py migrate`
   - `python manage.py createsuperuser` (opcional)
   - `python manage.py runserver` (localhost:8000)
- Tests: `pytest -q` (uses `pytest-django`; `pytest.ini` sets `DJANGO_SETTINGS_MODULE`).
- Conventions in this repo:
   - app `auditoria` contains models `Audit` e `Finding` (exemplos de campos e escolhas).
   - Use SQLite for local development; use env vars for secrets in production.

### API (Django REST Framework)

- The project exposes a minimal REST API using `djangorestframework` under `/api/`:
   - `GET /api/audits/` — list audits
   - `GET /api/audits/<id>/` — audit detail (includes nested `findings`)
   - `GET /api/findings/` — list findings
   - `GET /api/findings/<id>/` — finding detail
- Serializer examples: `auditoria/serializers.py` (nested `FindingSerializer` in `AuditSerializer`).
- ViewSets and router: `auditoria/api.py` and registered in `projeto_auditoria/urls.py` as `path('api/', ...)`.

### PAF (Plano Anual de Fiscalização)

- New app `paf` implements PAF functionality. Key files:
   - `paf/models.py` — `UnidadeTecnica`, `PAFAction`, `PAFImport`.
   - `paf/admin.py` — admin registration for easy management.
   - `paf/migrations/` — initial DB schema, applied locally.
- Dependencies: `openpyxl` is added to `requirements.txt` to parse `.xlsx` files.

Design notes for agents:

- Use `PAFImport` to store uploaded files and track processing results (`summary` JSON field) and `uploaded_by` for audit.
- Implement import flow: validate sheet columns and row-level constraints, collect per-line errors, process valid rows and persist errors into the `summary` of `PAFImport` for UX reporting.
- When importing a PAF for a year where existing actions exist, prompt the user to either replace the full plan (if no action is in execution) or merge new actions while preserving existing ones (match by `codigo_acao`).




## Examples of useful, repository-specific tasks an agent can propose or perform ✍️
- If maintainers confirm this is a Python web app: propose creating `README.md` with setup steps, `requirements.txt` (or `pyproject.toml`), and a `tests/` folder with a tiny smoke test.
- If repository should be empty (placeholder), add a short note in `README.md` and open an issue describing what is expected to be added.

## Communication & PR conventions for AI agents 🧾
- Create small focused PRs and reference the issue that documents the discovery. Include explicit reproduction steps and how you verified behavior in the PR description.
- If unsure about an assumption (framework, required service), open an issue before making non-trivial changes and tag maintainers.

---

If you'd like, I can: (1) create a minimal `README.md` and a small smoke test now, or (2) open an issue draft that summarizes the missing elements and asks maintainers how they'd like to proceed. Which should I do next? 

<!-- End of autogenerated copilot-instructions.md -->