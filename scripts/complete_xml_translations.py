#!/usr/bin/env python3
"""Fill missing translations in Excel 2003 XML using LibreTranslate.

- Removes ss:Index jumps and normalizes each row to 14 cells (key + 13 languages).
- Uses English (column 3) as the only source; if English is missing, the row is skipped.
- Never changes German (column 2); only translates into the remaining languages.
- Calls LibreTranslate for empty cells (or cells equal to the English source) and writes the file back (unless --dry-run).
"""

import argparse
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Dict, Tuple

from lxml import etree

NS_SS = "urn:schemas-microsoft-com:office:spreadsheet"
NS_HTML = "http://www.w3.org/TR/REC-html40"

q = lambda t: f"{{{NS_SS}}}{t}"

LANG_COLUMNS = [
    ("ger", "de"),
    ("eng", "en"),
    ("ned", "nl"),
    ("fra", "fr"),
    ("ita", "it"),
    ("esp", "es"),
    ("chi", "zh-Hans"),  # simplified Chinese matches LibreTranslate code
    ("fas", "fa"),
    ("rus", "ru"),
    ("hin", "hi"),
    ("ara", "ar"),
    ("vie", "vi"),
    ("heb", "he"),
]

TOTAL_COLS = 14  # key + 13 languages


def fetch_supported_targets(source: str, base_url: str):
    """Return a set of target language codes supported from the given source.

    Falls back to None on error to avoid blocking the script; callers should
    interpret None as "unknown, attempt anyway".
    """
    try:
        with urllib.request.urlopen(f"{base_url.rstrip('/')}/languages", timeout=10) as resp:
            body = resp.read()
            data = json.loads(body)
    except Exception as exc:  # pragma: no cover - network dependent
        print(f"[warn] could not fetch supported language list: {exc}", file=sys.stderr)
        return None

    targets = set()
    for entry in data:
        code = entry.get("code") or entry.get("source")
        if code != source:
            continue
        # two possible schemas: {code, targets[]} or {source, target}
        for tgt in entry.get("targets", []):
            targets.add(tgt)
        tgt_single = entry.get("target")
        if tgt_single:
            targets.add(tgt_single)
    return targets


def translate(text: str, source: str, target: str, base_url: str, cache: Dict[Tuple[str, str, str], str], timeout: float) -> str:
    key = (text, source, target)
    if key in cache:
        return cache[key]
    payload = {
        "q": text,
        "source": source,
        "target": target,
        "format": "text",
    }
    data = urllib.parse.urlencode(payload).encode("utf-8")
    req = urllib.request.Request(f"{base_url.rstrip('/')}/translate", data=data)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read()
            parsed = json.loads(body)
            out = parsed.get("translatedText")
            if not out:
                raise RuntimeError(f"Empty translation for target={target}")
            cache[key] = out
            return out
    except Exception as exc:  # pragma: no cover - network dependent
        raise RuntimeError(f"Translation failed for target={target}: {exc}")


def normalize_cells(row: etree._Element) -> None:
    cells_orig = row.findall(q("Cell"))
    new_cells = []
    pos = 1
    for cell in cells_orig:
        idx_attr = cell.get(f"{{{NS_SS}}}Index")
        if idx_attr:
            idx = int(idx_attr)
            while pos < idx:
                filler = etree.Element(q("Cell"))
                new_cells.append(filler)
                pos += 1
            cell.attrib.pop(f"{{{NS_SS}}}Index", None)
        new_cells.append(cell)
        pos += 1
    while len(new_cells) < TOTAL_COLS:
        new_cells.append(etree.Element(q("Cell")))
    if len(new_cells) > TOTAL_COLS:
        del new_cells[TOTAL_COLS:]
    row[:] = new_cells


def ensure_data(cell: etree._Element) -> etree._Element:
    data = cell.find(q("Data"))
    if data is None:
        data = etree.SubElement(cell, q("Data"))
        data.set(f"{{{NS_SS}}}Type", "String")
    return data


def fill_translations(path: Path, base_url: str, dry_run: bool, timeout: float, sleep: float) -> int:
    parser = etree.XMLParser(remove_blank_text=False)
    tree = etree.parse(str(path), parser)
    table = tree.find(f".//{q('Table')}")
    if table is None:
        raise SystemExit("No Table element found")
    rows = table.findall(q("Row"))
    cache: Dict[Tuple[str, str, str], str] = {}
    supported_targets = fetch_supported_targets("en", base_url)
    unsupported_logged = set()
    failed_pairs = set()
    updated_rows = 0
    for ridx, row in enumerate(rows):
        cells = row.findall(q("Cell"))
        if not cells:
            continue
        key_data = cells[0].find(q("Data"))
        key = key_data.text if key_data is not None else None
        if key in (None, "LOCALE") or ridx == 0:
            continue
        normalize_cells(row)
        cells = row.findall(q("Cell"))
        ger_cell = cells[1] if len(cells) > 1 else None
        eng_cell = cells[2] if len(cells) > 2 else None
        ger_data = ger_cell.find(q("Data")) if ger_cell is not None else None
        eng_data = eng_cell.find(q("Data")) if eng_cell is not None else None
        ger_text = ger_data.text if ger_data is not None else None
        eng_text = eng_data.text if eng_data is not None else None

        # use English only as source; keep German untouched
        source_text = eng_text if eng_text and eng_text.strip() else None
        source_code = "en"

        if not source_text or not source_text.strip():
            continue
        changed = False
        for col_idx, (_, target_code) in enumerate(LANG_COLUMNS[2:], start=3):
            if target_code == source_code:
                continue
            if supported_targets is not None and target_code not in supported_targets:
                if target_code not in unsupported_logged:
                    print(f"[info] skipping target={target_code} (not supported by source=en according to /languages)", file=sys.stderr)
                    unsupported_logged.add(target_code)
                continue
            cell = cells[col_idx]
            data = cell.find(q("Data"))
            text = data.text if data is not None else ""
            needs_translation = text is None or not str(text).strip() or str(text).strip() == source_text.strip()
            if needs_translation:
                try:
                    translated = translate(source_text, source_code, target_code, base_url, cache, timeout)
                except RuntimeError as exc:
                    pair = (source_code, target_code)
                    if pair not in failed_pairs:
                        print(f"[warn] row {ridx} key={key}: {exc}", file=sys.stderr)
                        failed_pairs.add(pair)
                    continue
                if sleep:
                    time.sleep(sleep)
                data = ensure_data(cell)
                data.text = translated
                changed = True
        if changed:
            updated_rows += 1
    if not dry_run:
        tree.write(str(path), xml_declaration=True, encoding="utf-8")
    return updated_rows


def main() -> int:
    ap = argparse.ArgumentParser(description="Fill missing translations via LibreTranslate")
    ap.add_argument("--base-url", default="http://localhost:5000", help="LibreTranslate base URL")
    ap.add_argument("--file", default="Products/zms/import/_language.xml", help="Path to Excel XML file")
    ap.add_argument("--dry-run", action="store_true", help="Do not write file, just report")
    ap.add_argument("--timeout", type=float, default=30.0, help="HTTP timeout seconds")
    ap.add_argument("--sleep", type=float, default=0.0, help="Optional sleep between calls (seconds)")
    args = ap.parse_args()

    path = Path(args.file)
    if not path.exists():
        print(f"File not found: {path}", file=sys.stderr)
        return 1
    try:
        updated = fill_translations(path, args.base_url, args.dry_run, args.timeout, args.sleep)
        mode = "dry-run" if args.dry_run else "written"
        print(f"Updated rows: {updated} ({mode})")
    except Exception as exc:  # pragma: no cover - top-level safety
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
