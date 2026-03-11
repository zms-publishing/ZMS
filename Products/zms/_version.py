from pathlib import Path

_raw = Path(__file__).with_name("version.txt").read_text(encoding="utf-8").strip()
__version__ = _raw.split("+", 1)[0]