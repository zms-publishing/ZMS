# ZMS Action "Search and Replace"

## For Users

### Purpose

The **Search and Replace** action lets you scan the current content tree for text matches and optionally replace them.

It is available for:

- `ZMSDocument`
- `ZMSObject`

Roles allowed by default:

- `ZMSAdministrator`
- `ZMSEditor`
- `ZMSAuthor`

### How to use it

1. Open the page/folder where you want to start the search.
2. Run **Search and Replace...** from the metacommands.
3. Enter **Search for** text.
4. Optional: enter **Replace with** text.
5. Optional: enable **Attribute Filter** and select:
   - content class
   - attribute
   - language
6. Choose whether the search should be case-sensitive.
7. Click **Execute**.

### Safe workflow (recommended)

1. Keep the **Replace with** checkbox disabled.
2. Run a search-only pass and review the result list.
3. Enable replacement and run again only after verification.

This gives you a dry-run before changing content.

### What happens after execution

- The result panel shows how many matches were found.
- Each result links to the matching object in a new tab.
- The preview highlights matched and replacement text.
- If replacement is enabled, matching values are written immediately.

### Notes and limitations

- Search is recursive through child nodes.
- `ZMSLinkElement` children are skipped intentionally.
- Only non-empty values are checked.
- Replacements affect text values and also list/dict payloads where possible.

---

## For Developers

### Files and registration

- Definition: `Products/zms/conf/metacmd_manager/manage_searchReplace/__init__.yaml`
- Implementation: `Products/zms/conf/metacmd_manager/manage_searchReplace/manage_searchReplace.py`

The metacommand points to the external method `manage_searchReplace`.

### Request parameters

Main parameters consumed by `manage_searchReplace(self)`:

- `old`: search value
- `new`: replacement value
- `upperlower`: `1` for case-sensitive mode
- `replace`: `1` to persist replacements
- `filter`: `1` to enable class/attribute/language filter
- `cselected`: selected content class
- `aselected`: selected attribute id
- `lselected`: selected language id
- `mode`: `html` (default) or `ajax`

`mode=ajax` returns only the attribute selector HTML for dynamic UI updates.

### Core flow

1. Build UI and read request state.
2. On `BTN_EXECUTE`, call `run(context, old, new)`.
3. Traverse current node and child nodes recursively.
4. For each attribute value:
   - compute `newVal = replace(objAttrVal, old, new)`
   - if changed and `replace=1`, persist via `operator_setattr(...)`
   - collect a result entry for reporting
5. Render result summary and detailed hit list.

### Replacement behavior

`replace(o, old, new)` handles multiple payload types:

- `str` / `bytes`: direct replacement
- `dict`: recursive replacement on values
- `list`: recursive replacement on items

Case modes differ intentionally:

- case-sensitive: `o.replace(old, new)` (literal)
- case-insensitive: `re.sub(re.compile(old, re.IGNORECASE), new, o)`

### Important caveats

- In case-insensitive mode, `old` is treated as a regex pattern.
  Special regex characters are not escaped automatically.
- Invalid regex patterns can raise `re.error`.
- Empty values are skipped (`if objAttrVal:`), so empty strings are not processed.
- Type mismatches (for example `bytes` with string pattern) can raise `TypeError`; the code logs and keeps the original value.
- Replacements are in-memory object changes through ZMS accessors; no extra commit logic is implemented here.

### UI implementation details

- Output is generated as HTML strings in `renderHtml()`.
- jQuery is used for:
  - enabling/disabling filter controls
  - case indicator updates
  - AJAX reload of attribute selector (`ajaxAttrSelector`)
  - loader visibility during form submit
- Result preview uses tooltip markup with highlighted before/after fragments.

### Extension points

Common places to adapt behavior:

- Make case-insensitive search literal by using `re.escape(old)`.
- Add explicit regex mode (separate checkbox) instead of implicit regex behavior.
- Precompile pattern once per request for performance.
- Add include/exclude rules per meta type.
- Add structured output mode (for example JSON) for automation.
