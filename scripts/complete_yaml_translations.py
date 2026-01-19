#!/usr/bin/env python3
"""Complete incomplete translations in YAML language file using LibreTranslate.

- Reads YAML file with technical terms and their translations
- Uses English (eng) as the source for missing translations
- Fills in missing languages for each term
- Writes updated YAML back to file (unless --dry-run)
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

ALL_LANG_NAMES = {lang_name for lang_name, _ in LANG_COLUMNS}


def fetch_supported_targets(source: str, base_url: str):
    """Return a set of target language codes supported from the given source."""
    try:
        with urllib.request.urlopen(f"{base_url.rstrip('/')}/languages", timeout=10) as resp:
            body = resp.read()
            data = json.loads(body)
    except Exception as exc:
        print(f"[warn] could not fetch supported language list: {exc}", file=sys.stderr)
        return None

    targets = set()
    for entry in data:
        code = entry.get("code") or entry.get("source")
        if code != source:
            continue
        for tgt in entry.get("targets", []):
            targets.add(tgt)
        tgt_single = entry.get("target")
        if tgt_single:
            targets.add(tgt_single)
    return targets


def translate(text: str, source: str, target: str, base_url: str, cache: Dict[Tuple[str, str, str], str], timeout: float) -> str:
    """Translate text using LibreTranslate API."""
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
    except Exception as exc:
        raise RuntimeError(f"Translation failed for target={target}: {exc}")


def parse_yaml_simple(content: str) -> Dict[str, Dict[str, str]]:
    """Simple YAML parser for our specific format."""
    entries = {}
    current_key = None
    
    for line in content.split('\n'):
        # Skip empty lines
        if not line.strip():
            continue
        
        # Level 1: Technical term (no leading spaces, ends with :)
        if line and not line.startswith(' ') and line.endswith(':'):
            current_key = line[:-1]  # Remove trailing :
            entries[current_key] = {}
        # Level 2: Language translations (starts with 2 spaces)
        elif line.startswith('  ') and current_key:
            # Parse "  lang: value"
            parts = line.strip().split(':', 1)
            if len(parts) == 2:
                lang_name = parts[0].strip()
                value = parts[1].strip()
                entries[current_key][lang_name] = value
    
    return entries


def write_yaml(entries: Dict[str, Dict[str, str]], output_path: Path):
    """Write entries to YAML file."""
    lines = []
    
    for key in sorted(entries.keys()):
        lines.append(f"{key}:")
        translations = entries[key]
        
        # Write languages in the order defined in LANG_COLUMNS
        for lang_name, _ in LANG_COLUMNS:
            if lang_name in translations:
                value = translations[lang_name]
                lines.append(f"  {lang_name}: {value}")
        
        lines.append("")  # Blank line between entries
    
    output_path.write_text("\n".join(lines), encoding="utf-8")


def complete_translations(yaml_path: Path, base_url: str, dry_run: bool, timeout: float, sleep: float) -> Tuple[int, int]:
    """Complete missing translations in YAML file."""
    content = yaml_path.read_text(encoding="utf-8")
    entries = parse_yaml_simple(content)
    
    cache: Dict[Tuple[str, str, str], str] = {}
    supported_targets = fetch_supported_targets("en", base_url)
    unsupported_logged = set()
    failed_pairs = set()
    
    incomplete_count = 0
    updated_count = 0
    
    for key, translations in entries.items():
        # Check if English is present
        eng_text = translations.get("eng", "").strip()
        if not eng_text:
            continue
        
        # Check for missing languages
        missing_langs = []
        for lang_name, lang_code in LANG_COLUMNS:
            if lang_name == "eng":
                continue  # Skip English itself
            
            current_value = translations.get(lang_name, "").strip()
            # Need translation only if missing or empty
            if not current_value:
                missing_langs.append((lang_name, lang_code))
        
        if not missing_langs:
            continue  # This entry is complete
        
        incomplete_count += 1
        changed = False
        
        # Translate missing languages
        for lang_name, lang_code in missing_langs:
            # Skip if not supported
            if supported_targets is not None and lang_code not in supported_targets:
                if lang_code not in unsupported_logged:
                    print(f"[info] skipping target={lang_code} (not supported by source=en)", file=sys.stderr)
                    unsupported_logged.add(lang_code)
                continue
            
            try:
                translated = translate(eng_text, "en", lang_code, base_url, cache, timeout)
                entries[key][lang_name] = translated
                changed = True
                
                if sleep:
                    time.sleep(sleep)
            except RuntimeError as exc:
                pair = ("en", lang_code)
                if pair not in failed_pairs:
                    print(f"[warn] key={key}: {exc}", file=sys.stderr)
                    failed_pairs.add(pair)
                continue
        
        if changed:
            updated_count += 1
    
    # Write back to file
    if not dry_run and updated_count > 0:
        write_yaml(entries, yaml_path)
    
    return incomplete_count, updated_count


def main() -> int:
    ap = argparse.ArgumentParser(description="Complete missing translations in YAML via LibreTranslate")
    ap.add_argument("--base-url", default="http://localhost:5000", help="LibreTranslate base URL")
    ap.add_argument("--file", default="Products/zms/import/_language.yaml", help="Path to YAML file")
    ap.add_argument("--dry-run", action="store_true", help="Do not write file, just report")
    ap.add_argument("--timeout", type=float, default=30.0, help="HTTP timeout seconds")
    ap.add_argument("--sleep", type=float, default=0.0, help="Optional sleep between calls (seconds)")
    args = ap.parse_args()

    yaml_path = Path(args.file)
    if not yaml_path.exists():
        print(f"File not found: {yaml_path}", file=sys.stderr)
        return 1
    
    try:
        incomplete, updated = complete_translations(yaml_path, args.base_url, args.dry_run, args.timeout, args.sleep)
        mode = "dry-run" if args.dry_run else "written"
        print(f"Incomplete entries: {incomplete}")
        print(f"Updated entries: {updated} ({mode})")
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
