"""
_version.py

Provides core utilities for version lifecycle, publication flow, and semantic versioning.
It manages draft/live transitions, version numbering, approval workflows, and content staging.

License: GNU General Public License v2 or later,
Organization: ZMS Publishing
"""
from pathlib import Path

_raw = Path(__file__).with_name("version.txt").read_text(encoding="utf-8").strip()
__version__ = _raw.split("+", 1)[0]