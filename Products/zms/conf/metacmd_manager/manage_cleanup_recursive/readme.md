# manage_cleanup_recursive — Listing and Removal of Obsolete Inactive Content

**Version:** 0.8.1  
**Role Required:** ZMSAdministrator  
**Icon:** <i class="fas fa-trash-alt text-primary"></i> (trash can)

## What It Does

The `manage_cleanup_recursive` metacommand is a comprehensive content lifecycle management tool that:

- **Identifies** inactive or old content across your entire document tree
- **Grades** content for deletion or manual review based on activation status and age
- **Prevents accidental deletion** of content with active sub-pages (intelligent validation)
- **Manifests results** in multiple formats: interactive HTML, JSON, or CSV
- **Supports batch operations** to delete old content or refresh edit dates on demand
- **Respects multilingual content** — evaluates each language variant separately

Perfect for maintaining large ZMS installations by automating the cleanup of outdated documentation or archived sections.

---

## How It Works

### 1. Content Grading Logic

The tool scans every page and language variant in your document tree and assigns a **grading value**:

- **Grade 0 (Ignore):** Content is currently active in one or more languages — not marked for any action
- **Grade 1 (Check):** Content is inactive (archived or disabled) and has been inactive for a certain period — flagged for manual review
- **Grade 2 (Delete):** Content is inactive AND all sub-pages are also inactive or missing — candidate for deletion

### 2. Validation & Safeguards

Before marking content for deletion, the tool performs validation:

1. **Sub-page Safety Check**: A node marked Grade 2 is automatically downgraded to Grade 1 (Check) if ANY of its sub-pages in the document tree is currently active
2. **Language Filtering**: Only primary language variants are queued for deletion (prevents accidental removal of language-specific content)
3. **Orphan Detection**: Content with active children stays in the "Check" list, never gets deleted

This two-stage approach (grading → validation) ensures you never accidentally delete content that has any active or important children.

### 3. Multi-Language Support

The tool evaluates each language separately:

- Every language variant of every page receives its own grading
- Deletion candidates must be from the **primary language** and have matching **language coverage**
- Heterolingual items (non-primary language, different coverage) are excluded from deletion lists

---

## Getting Started

### Accessing the Tool in the ZMS Admin Interface

1. Log into ZMS with administrator credentials
2. Navigate to **Metadata** → **Metacommands** tab (in the folder/site properties)
3. Find **"Remove inactive content"** in the metacommands table
4. Click the **question mark icon** (<i class="far fa-question-circle text-info"></i>) in the **Readme** column to open this guide
5. Or click directly on the metacommand title to execute it

### Initial Execution

When you click the metacommand:

1. A **spinner page** loads while processing begins
2. The tool scans your entire document tree (can take 10–60 seconds depending on tree size)
3. Results display in an **interactive HTML dashboard**

### Understanding the Results Dashboard

#### Overview Bar

Shows processing metadata:

- **Page Count**: Total pages scanned (including root site)
- **Language Count**: Total language variants processed
- **Processing Time**: Duration in seconds (for performance monitoring)

#### DELETE Section (Red)

Lists content **recommended for deletion**:

- **Title & Link**: Click to view the page in the admin interface
- **ID**: Object path (e.g., `/content/old_section`)
- **Language**: Which language variant this entry represents
- **Years**: Age in years since last edit
- **Trash Icon**: Click to move to Trashcan immediately
- **Refresh Icon**: Click to update the edit date to now (useful to "save" a page from deletion)

#### CHECK Section (Blue)

Lists content **flagged for manual review**:

- Same columns as DELETE section
- These items are **not automatically deleted** — they require your decision
- Use trash/refresh icons to take action on specific items

#### Success Message

If no items appear in either section, all content is either active or has active children — nothing needs cleanup.

---

## Output Formats

The tool supports three output modes (see query parameters below):

### HTML (Default)

Interactive dashboard with:
- Sortable lists with age information
- Individual delete/refresh buttons per item
- Real-time HTMX-powered operations
- Visual color-coding (red for delete, blue for check)

**Usage:**
```
manage_cleanup_recursive?lang=ger
```

### JSON

Raw grading data for programmatic processing:

**Usage:**
```
manage_cleanup_recursive?content_type=json
```

**Output Structure:**
```json
[
  {
    "zmsid": "object_id",
    "title": "Page Title",
    "absolute_url": "/content/path",
    "lang": "ger",
    "primary_lang": "ger",
    "age_days": 1234,
    "grading": 2,
    "grading_info": "DELETE",
    "is_multilang_inactive": true,
    "obj_path": ["Home", "Section", "object_id"],
    "coverage": "ger"
  }
]
```

**Use Cases:**
- Export to external analytics systems
- Build custom dashboards
- Integrate with backup systems (archive before deletion)
- Debug grading decisions

### CSV

Tabular export with deletion and check candidates:

**Usage:**
```
manage_cleanup_recursive?content_type=csv
```

**Output Structure:**
```
INFO	TITLE	URL	LANGUAGE	AGE/YEARS
DELETE	Old Newsletter	http://example.com/...	ger	3
DELETE	Archived Docs	http://example.com/...	ger	5
SEPARATOR
CHECK	Inactive But Has Active Child	http://example.com/...	ger	2
```

**Use Cases:**
- Import into spreadsheets (Excel, Google Sheets)
- Generate reports for stakeholders
- Prepare batch deletion lists for review

---

## Operations

### Delete Operation

**What it does:** Moves a page to the ZMS Trashcan (can be restored from there)

**Trigger:**
- Click the **trash icon** (<i class="far fa-trash-alt text-danger"></i>) in the HTML dashboard
- Or call: `manage_cleanup_recursive?do_delete=1&delete_url=/path/to/page&lang=ger`

**Safety:**
- Requires confirmation dialog
- Only removes the page itself, not sub-pages (they stay in document tree)
- Page moves to Trashcan — not permanently deleted

### Refresh Operation

**What it does:** Updates the page's edit date to the current time

**Trigger:**
- Click the **calendar icon** (<i class="fas fa-calendar-check text-primary"></i>) in the HTML dashboard
- Or call: `manage_cleanup_recursive?do_refresh=1&refresh_url=/path/to/page&lang=ger`

**Use Cases:**
- "Rescue" a page from being marked for deletion
- Mark content as still relevant (without moving/editing it)
- Bulk refresh dates for a section you want to keep

### Check Operation

**What it does:** Evaluates and displays a list of check-grade items

**Trigger:**
- Scroll to the blue **CHECK** section in the HTML dashboard
- Or extract from JSON output

**Decision Options:**
- Leave it (no action needed if it has active children)
- Delete it (use trash icon if you're confident)
- Refresh it (use calendar icon to extend its life)

---

## Query Parameters

Control tool behavior and output:

| Parameter | Values | Default | Effect |
|-----------|--------|---------|--------|
| `lang` | Language code (e.g., `ger`, `eng`) | Primary language | Which language variant to process |
| `content_type` | `html` \| `json` \| `csv` | `html` | Output format |
| `do_execution` | `0` \| `1` | `0` | Skip spinner (internal) |
| `do_delete` | `1` | (none) | Execute delete operation on `delete_url` |
| `delete_url` | Page path | (required with `do_delete`) | Which page to delete |
| `do_refresh` | `1` | (none) | Execute refresh operation on `refresh_url` |
| `refresh_url` | Page path | (required with `do_refresh`) | Which page to refresh |

**Example URLs:**
```
# Export as CSV
.../manage_cleanup_recursive?content_type=csv

# Export as JSON
.../manage_cleanup_recursive?content_type=json

# Delete a specific page (with confirmation)
.../manage_cleanup_recursive?do_delete=1&delete_url=/content/old_page&lang=ger

# Refresh a page (mark as current)
.../manage_cleanup_recursive?do_refresh=1&refresh_url=/content/old_page&lang=ger
```

---

## Customization & Extension Points

### Adapting Cleanup Grading Logic

The core grading decision is made in the `get_cleanup_grading()` function. Customize it to fit your content model:

**Location:** `manage_cleanup_recursive.py` (search for `def get_cleanup_grading`)

**Key Data Available:**

```python
def get_cleanup_grading(page, request):
    # Returns dictionary with:
    # - zmsid: Object ID
    # - title: Page title
    # - age_days: Days since last modification
    # - is_multilang_inactive: Whether marked inactive in current language
    # - lang: Current language
    # - primary_lang: Site's primary language
    # - coverage: Language coverage setting
    # - absolute_url: URL path
    # - obj_path: Breadcrumb path as list
```

**Customization Examples:**

1. **Change age threshold** (default: unclear from code, likely 365+ days):
   - Modify the condition that calculates `age_days`
   - Or adjust the comparison in validation logic

2. **Exclude specific content types**:
   ```python
   if page.meta_id in ['ZMSMediaAsset', 'ZMSLinkTarget']:
       return grading_as_ignore()
   ```

3. **Mark for deletion based on custom criteria**:
   - Check custom metadata fields (`getDomainProperties()`)
   - Inspect content size or last access logs
   - Read custom deletion flags

4. **Grade by pattern** (e.g., URLs containing "archive" or "draft"):
   ```python
   if 'archive' in page.absolute_url().lower():
       return grading_as_grade_2()
   ```

### Bulk Operations via JSON Export

Export the JSON output and process programmatically:

```python
# Pseudo-code: Bulk refresh all CHECK items in a report
import json
import requests

report = requests.get('http://site/manage_cleanup_recursive?content_type=json').json()
check_items = [e for e in report if e['grading'] == 1]

for item in check_items:
    refresh_url = item['absolute_url']
    requests.post(
        f'http://site/manage_cleanup_recursive',
        data={'do_refresh': '1', 'refresh_url': refresh_url, 'lang': item['lang']}
    )
```

---

## Multilingual Content Handling

### Language Coverage Field

The tool respects the `coverage` field (set per page and language):

- `coverage = "ger"` → Page is for **German only**
- `coverage = "all"` → Page is for **multiple languages**

**Deletion Rule:**
Only pages where `lang == primary_lang` AND `coverage.endswith(lang)` are queued for deletion.

**Example:**

| Title | Lang | Primary | Coverage | Grading | Marked for Delete? |
|-------|------|---------|----------|---------|------------------|
| Page A | ger | ger | ger | Grade 2 | ✅ YES |
| Page A | eng | ger | eng | Grade 2 | ❌ NO (not primary lang) |
| Page A | ger | ger | all | Grade 2 | ❌ NO (coverage is "all") |

This ensures you don't accidentally delete language-specific versions or global content marked for multiple languages.

---

## Safety & Best Practices

### Before Running

1. **Backup Your Database**
   - Always create a full ZODB backup before large cleanups
   - The tool uses the Trashcan (recoverable), but backups are insurance

2. **Test on a Copy**
   - Run the tool on a staging instance first
   - Export CSV/JSON results to review
   - Validate grading decisions match your expectations

3. **Review the CHECK List First**
   - Run with `content_type=csv` or `content_type=json`
   - Manually review items marked for deletion
   - Identify false positives (e.g., content that should stay)

### During Execution

1. **Use DELETE Only for Obvious Candidates**
   - First-time cleanup: use CHECK only
   - Only bulk-delete on subsequent runs after validation

2. **Refresh Before Deleting**
   - If unsure about a page, click refresh (update edit date)
   - It will re-evaluate on the next run

3. **Check Sub-Pages**
   - Click linked pages to verify they don't have active children
   - The validation logic prevents deletion, but you should double-check

### After Execution

1. **Empty the Trashcan Periodically**
   - Deleted pages sit in Trashcan and consume storage
   - Empty after confirming deletions were correct

2. **Document What You Cleaned**
   - Keep records of deleted content (for compliance/audit trails)
   - Export JSON/CSV reports for archival

3. **Schedule Regular Cleanups**
   - Monthly or quarterly: run the tool to identify new candidates
   - Annual or biennial: bulk delete validated candidates

---

## Troubleshooting

### Issue: "No items to check" but I know there's old content

**Causes & Solutions:**

1. **Content is technically "active"**
   - Check the `is_archived` or `active` flags in ZMS object properties
   - If not explicitly disabled, it's considered active

2. **Content is too recent**
   - Run `manage_cleanup_recursive?content_type=json` to see actual `age_days`
   - Adjust threshold expectations (e.g., 1-year-old content might not qualify)

3. **Language coverage prevents deletion**
   - Check the `coverage` field of candidate pages
   - Only "ger" + primary_lang matches are queued for deletion

**Fix:** Explicitly mark content as inactive in its language variant, then re-run.

---

### Issue: A page I want to keep is marked for deletion

**Causes & Solutions:**

1. **Grading Logic Mismatch**
   - Review the page's `is_multilang_inactive` status
   - If it should not be inactive, update it in the page properties

2. **Safe Recovery**
   - Delete the page (moves to Trashcan)
   - Immediately restore it from Trashcan
   - Edit the page (refresh edit date)
   - Re-run the tool

---

### Issue: Processing takes too long

**Causes & Solutions:**

1. **Large Document Tree**
   - The tool scans every page and language variant
   - For 10,000+ pages, expect 30–60 seconds

2. **Database Performance**
   - Check ZMS server logs for slow queries
   - Run during off-peak hours

3. **CSV/JSON Export is Slow**
   - Large datasets (10,000+ items) take time to serialize
   - Use JSON for larger exports (more efficient than HTML rendering)

**Optimization:**
- Consider running against a specific folder instead of root (if supported)
- Export to JSON first, process offline

---

### Issue: Delete or Refresh operations fail silently

**Causes & Solutions:**

1. **Check Browser Console**
   - Open Developer Tools (F12) and check the Console tab
   - Look for HTMX error messages

2. **Permission Issue**
   - Verify you're logged in as ZMSAdministrator
   - Some pages may have restricted ACLs

3. **Database Transaction Issue**
   - Check ZMS logs for ZODB transaction errors
   - Try refreshing the page and retrying

**Workaround:**
- Use query parameters directly: `manage_cleanup_recursive?do_delete=1&delete_url=/content/page&lang=ger`
- Refresh the page manually after each operation

---

### Issue: Grading results differ between runs

**Common Reasons:**

1. **Content was activated/deactivated between runs**
   - Expected behavior — grading reflects current state

2. **Multilingual coverage changed**
   - If you edited `coverage` field, results will differ

3. **Sub-page status changed**
   - A page might move from "Grade 2 (Delete)" to "Grade 1 (Check)" if a child was activated

**Solution:** This is normal. Re-run the tool to get current assessment.