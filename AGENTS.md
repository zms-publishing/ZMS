# AGENTS.md

## Repository Overview

ZMS is a Python-based Content Management and E-Publishing System built on top of the [Zope](https://zope.dev/) application server. It targets Science, Technology and Medicine (STM) publishing and provides a flexible content model with multilingualism, metadata, XML import/export, workflow, and more.

- **Package name:** `ZMS` (importable as `Products.zms`)
- **Python:** 3.10–3.14
- **Framework:** Zope 6 / WSGI
- **License:** GPL v3

## Repository Layout

```
Products/zms/          # Main package source
  conf/                # Default configuration files
  plugins/             # Pluggable components (RTE, file upload, …)
  skins/               # ZMI skin resources (CSS, JS, images)
  zpt/                 # Zope Page Templates (ZMI views)
  *.py                 # Core Python modules
tests/                 # pytest test suite
docs/                  # Markdown documentation chapters
docker/                # Docker build files
.github/workflows/     # CI workflows
```

## Setting Up a Development Environment

```bash
# Create and activate a virtual environment
python3 -m venv ~/ZMS
source ~/ZMS/bin/activate

# Editable install (recommended for development)
pip install --use-pep517 --config-settings editable_mode=compat -e .

# Install development extras (pytest, selenium, debugpy, …)
pip install -e ".[dev]"
```

> **Note:** Tests import Zope/OFS modules, so a fully installed Zope environment is required. Running `pytest` without Zope installed will fail.

## Running Tests

```bash
pytest ./tests/
```

Run a single test file:

```bash
pytest ./tests/test_standard.py
```

The CI matrix runs tests on Python 3.10–3.14 on Ubuntu. Tests are triggered on every push, pull request, weekly on Sundays, and can be triggered manually via `workflow_dispatch`.

## Code Conventions

- **Python style:** Follow PEP 8. The existing codebase uses 4-space indentation throughout.
- **Module naming:** Core helpers use a leading underscore (e.g. `_globals.py`, `_fileutil.py`). Public Zope content classes start with `ZMS` (e.g. `ZMSItem`, `ZMSWorkflowItem`).
- **Interfaces:** Defined in `IZMSxxx.py` files at the package root.
- **Templates:** Zope Page Templates live in `Products/zms/zpt/` and use the `.zpt` extension.
- **Configuration:** YAML-based configuration is handled via `ruamel.yaml`; XML import/export via `_xmllib.py`.
- **No new dependencies** should be added without a strong reason. Prefer the existing dependencies listed in `pyproject.toml`.

## Making Changes

1. Create a feature branch from `main`.
2. Make the smallest change that satisfies the requirement.
3. Add or update tests in `tests/` if the change affects logic.
4. Run the test suite locally before pushing (`pytest ./tests/`).
5. Push the branch and open a pull request targeting `main`.

## Releasing

Releases are published to PyPI via the GitHub Actions workflow `.github/workflows/pypi_publish.yml`. See `RELEASE.md` for the full release checklist and workflow details.

## Docker

A `docker-compose.yml` and `docker/` directory are provided for running ZMS in containers. See `docs/a_getting_started.md` for usage instructions.

## Documentation

Narrative documentation lives in `docs/`:

| File | Contents |
|------|----------|
| `a_getting_started.md` | Installation and first steps |
| `b_for_editors.md` | Content editing guide |
| `c_for_site_administrators.md` | Site administration |
| `d_for_developers.md` | Development environment, API, extending ZMS |
| `e_appendices.md` | Reference appendices |

API documentation is generated separately and published via the `.github/workflows/apidocs,yml` workflow.
