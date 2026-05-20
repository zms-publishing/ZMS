# ZMS Record Set

The **ZMS Record Set** is a tabular data type that stores structured records
(rows of key-value pairs) directly in the ZODB as a list of dictionaries.
It is not a standalone Python class but a special meta-object type handled
by the `ZMSCustom` framework — any object whose meta-type is defined as
`ZMSRecordSet` in the MetaObj Manager gains spreadsheet-like CRUD
capabilities.

## Core Concepts

| Concept | Description |
|---|---|
| **ZODB Storage** | Records are stored as a Python list of dictionaries in a ZODB object attribute — no external database required. |
| **Schema via MetaObj** | The column structure is defined in the ZMS MetaObj Manager as attributes of the record-set meta-object. |
| **Foreign Keys** | Columns can reference other record sets via FK relationships, rendered as dropdowns with navigation links. |
| **In-Memory Operations** | Filtering, sorting, and pagination all operate on the in-memory list — ideal for small to medium data sets. |
| **Multilingual** | Record sets force language to the primary language (`getPrimaryLanguage()`) and set `is_page_element = True`. |

## GUI Layout

### List View (`main` / `main_grid`)

The primary interface showing records in a paginated, sortable table:

- **Filter Bar** — session-stored filter criteria applied to any column
- **Column Headers** — clickable for sort-by-column (ascending/descending)
- **Checkboxes** — row selection for bulk operations
- **Action Buttons** — Insert, Update, Delete, Duplicate, Cut, Copy, Paste, Sort
- **Pagination** — page navigation for large record sets

### Grid Edit View (`grid`)

An inline-editable spreadsheet-style view:

- All records displayed in editable form fields
- Changes saved in bulk via `manage_changeRecordGrid()`
- Supports `_num_rows` for auto-expanding empty rows at the bottom
- Ideal for rapid data entry

### Record Form (`input_fields`)

A detailed single-record edit form:

- Each attribute rendered as the appropriate form control (text, select,
  image, richtext, etc.)
- FK columns rendered as dropdowns with navigation links to referenced records
- Nested record-set grids for sub-records
- Image preview with base64 display
- Insert / Update / Delete buttons

## API Reference

### Data Access

| Method | Returns | Description |
|---|---|---|
| `recordSet_Init(REQUEST)` | `list` | Load records from the ZODB attribute |
| `recordSet_Filter(REQUEST)` | `list` | Filter records by session-stored criteria and foreign key |
| `recordSet_Sort(REQUEST)` | `list` | Sort records by `_sort_id` or dynamic column/direction |

### CRUD Operations

| Method | Returns | Description |
|---|---|---|
| `manage_changeRecordSet(REQUEST)` | redirect | Full CRUD dispatcher: insert, update, delete, duplicate, and move records |
| `manage_changeRecordGrid(REQUEST)` | redirect | Save all inline grid edits at once |

### Import / Export

| Method | Returns | Description |
|---|---|---|
| `recordSet_Export(REQUEST, meta_id)` | `str` | Export records as XML or CSV |
| `recordSet_Import(REQUEST)` | — | Import records from XML data |

### Foreign Key Support

| Method | Returns | Description |
|---|---|---|
| `record_handler(meta_id, key)` | handler | Returns a handler that resolves FK references for display |

## Tips

- Record Sets are best suited for **small to medium data** (hundreds to low
  thousands of records). For larger datasets, consider the
  **ZMS SQL-DB Manager** which connects to external databases.
- Use the **Grid Edit** view for bulk data entry — it's much faster than
  editing records one by one.
- **Foreign Key** columns automatically render as dropdowns linking to
  the referenced record set — define them in the MetaObj Manager.
- Export to **CSV** for quick data exchange with spreadsheet applications.
- All record data lives in the ZODB, so it's included in standard ZODB
  backups and pack operations.
