#!/usr/bin/env python3
"""Convert Excel 2003 XML language file to YAML format.

Converts _language.xml to a YAML structure where:
- Level 1: technical term (key)
- Level 2: dictionary of language codes to translations
"""

import argparse
import sys
from pathlib import Path

from lxml import etree

NS_SS = "urn:schemas-microsoft-com:office:spreadsheet"

q = lambda t: f"{{{NS_SS}}}{t}"

LANG_COLUMNS = [
    ("ger", "de"),
    ("eng", "en"),
    ("ned", "nl"),
    ("fra", "fr"),
    ("ita", "it"),
    ("esp", "es"),
    ("chi", "zh-Hans"),
    ("fas", "fa"),
    ("rus", "ru"),
    ("hin", "hi"),
    ("ara", "ar"),
    ("vie", "vi"),
    ("heb", "he"),
]


def get_cell_text(cell):
    """Extract text from a cell element."""
    if cell is None:
        return ""
    data = cell.find(q("Data"))
    if data is None:
        return ""
    return data.text or ""


def convert_to_yaml(xml_path: Path, output_path: Path = None) -> str:
    """Convert Excel XML to YAML format."""
    parser = etree.XMLParser(remove_blank_text=False)
    tree = etree.parse(str(xml_path), parser)
    table = tree.find(f".//{q('Table')}")
    
    if table is None:
        raise SystemExit("No Table element found")
    
    rows = table.findall(q("Row"))
    
    # Build YAML content
    yaml_lines = []
    
    for ridx, row in enumerate(rows):
        cells = row.findall(q("Cell"))
        if not cells:
            continue
        
        # Get the key from first column
        key = get_cell_text(cells[0])
        
        # Skip header rows and empty keys
        if not key or key == "LOCALE" or ridx == 0:
            continue
        
        # Start the key entry
        yaml_lines.append(f"{key}:")
        
        # Add translations for each language (skip key column, index 0)
        for idx, (lang_name, lang_code) in enumerate(LANG_COLUMNS, start=1):
            if idx < len(cells):
                translation = get_cell_text(cells[idx])
                if translation:  # Only add non-empty translations
                    yaml_lines.append(f"  {lang_name}: {translation}")
        
        # Add blank line between entries for readability
        yaml_lines.append("")
    
    yaml_content = "\n".join(yaml_lines)
    
    # Write to file if output path specified
    if output_path:
        output_path.write_text(yaml_content, encoding="utf-8")
        print(f"Wrote {len(rows) - 1} entries to {output_path}")
    
    return yaml_content


def main() -> int:
    ap = argparse.ArgumentParser(description="Convert Excel XML language file to YAML")
    ap.add_argument(
        "--input",
        default="Products/zms/import/_language.xml",
        help="Path to Excel XML file"
    )
    ap.add_argument(
        "--output",
        default="Products/zms/import/_language.yaml",
        help="Path to output YAML file"
    )
    ap.add_argument(
        "--stdout",
        action="store_true",
        help="Print to stdout instead of file"
    )
    args = ap.parse_args()
    
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"File not found: {input_path}", file=sys.stderr)
        return 1
    
    try:
        if args.stdout:
            yaml_content = convert_to_yaml(input_path)
            print(yaml_content)
        else:
            output_path = Path(args.output)
            convert_to_yaml(input_path, output_path)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
