# ZMS SQL-DB Manager

The **SQL-DB Manager** (`ZMSSqlDb`) provides a full-featured SQL database
browser and editor within the ZMS management interface. It connects to
external relational databases via Zope Database Adapters and offers schema
introspection, CRUD operations, blob management, and a configurable
column model — all without leaving the ZMI.

## Core Concepts

| Concept | Description |
|---|---|
| **Database Adapter** | Connects to the database through a Zope Database Adapter (e.g. `Z MySQL`, `Z PostgreSQL`, `Z SQLite`). The adapter ID is stored as the `connection_id` property. |
| **Table Filter** | A regex pattern (`table_filter`) controlling which tables are visible in the management interface. |
| **Column Model** | An optional XML/DTML configuration (`model`) that customizes column display, stereotypes, and foreign key relationships beyond what schema introspection provides. |
| **Relation Target Resolver** | `getEntityTarget(...)` resolves effective relation targets for `details`/`multiselect`, including intersection-table mappings. |
| **Stereotypes** | Column type annotations controlling rendering and validation: `string`, `date`, `datetime`, `int`, `float`, `html`, `multiselect`, `multimultiselect`, `image`, `file`, `checkbox`, `password`, `richtext`, `text`, `amount`, `url`. |
| **Blob Storage** | Binary columns (images, files) are stored on the filesystem linked to the database row, not in the database itself. |
| **Event Hooks** | Insert, update, and delete operations fire `onChangeObj` events with patterns like `BeforeInsert`/`AfterInsert`, enabling custom triggers. |

## GUI Layout

### Edit Tab (`manage_main`)

The primary database browsing interface:

- **Table Selector** — dropdown listing all tables matching the `table_filter`
- **Filter Bar** — column-based filter criteria (stored in session)
- **Data Grid** — paginated, sortable table displaying query results
- **Action Buttons** — Insert, Update, Delete for record manipulation
- **Record Form** — detailed single-record edit form for insert/update

### Properties Tab (`manage_properties`)

Configuration form for the database connection:

- **Connection ID** — reference to the Zope Database Adapter
- **Charset** — character encoding (default: `utf-8`)
- **Table Filter** — regex pattern for visible tables
- **Model** — XML/DTML editor for custom column configuration

### Configuration Tab (`manage_configuration`)

Table and column configuration:

- **Table List** — all detected tables with their column definitions
- **Column Editor** — per-column settings: stereotype, FK references,
  display options, custom labels

## API Reference

### Connection & SQL

| Method | Returns | Description |
|---|---|---|
| `getDA()` | adapter | Returns the Zope Database Adapter object |
| `query(sql, max_rows)` | result | Execute SQL with parameter handling |
| `executeQuery(sql)` | `list[dict]` | Execute SELECT, return assembled result dicts |
| `executeSql(sql)` | `int` | Execute DML (INSERT/UPDATE/DELETE), return row count |
| `sql_quote__(tablename, key, val)` | `str` | SQL-safe quoting by column type |
| `sql_delimiter(tablename, key, val)` | `str` | Replace `?` placeholders with quoted values |

### Schema Introspection

| Method | Returns | Description |
|---|---|---|
| `getEntities()` | `list` | All table definitions (tries custom method → SQLAlchemy → introspection) |
| `getEntity(tablename)` | `dict` | Single table definition by name |
| `getEntityTarget(sourceTableName, targetTableName)` | `dict` | Resolves relation targets and unwraps intersection-table relations to the effective destination entity |
| `getEntityColumn(tablename, columnname)` | `dict` | Full column metadata including FK, blob, multiselect stereotypes |
| `getEntityPK(tablename)` | `str` | Primary key column name for a table |
| `getEntitiesSQLAlchemyDA()` | `list` | Schema introspection via SQLAlchemy |

### CRUD Operations

| Method | Returns | Description |
|---|---|---|
| `recordSet_Insert(tablename, values, REQUEST)` | `dict` | INSERT a row, handle auto-columns, blobs, FK, intersections |
| `recordSet_Update(tablename, rowid, values, REQUEST)` | `dict` | UPDATE a row with diff detection and blob handling |
| `recordSet_Delete(tablename, rowid, REQUEST)` | — | DELETE a row by primary key |

### Query Building

| Method | Returns | Description |
|---|---|---|
| `getEntityRecordHandler(tablename, stereotypes=None, colNames=None)` | object | Builds a row post-processor; when `colNames` is set, it still injects the primary key for row actions |
| `sql_record_init(tablename, REQUEST)` | — | Initialize SQL statement and request context |
| `sql_record_where(tablename, REQUEST)` | SQL | Build WHERE clause from session filters |
| `sql_record_order(tablename, REQUEST)` | SQL | Build ORDER BY clause |

### Grid Context & Rendering

| Method | Returns | Description |
|---|---|---|
| `getEntityDetailsGridContext(REQUEST)` | `dict` | Prepares detail-grid context (columns, records, URL params, and insert/update/delete actions) for `manage_zmi_details_grid` |

### Blob Management

| Method | Returns | Description |
|---|---|---|
| `getBlob(tablename, rowid, column)` | blob | Read a blob from filesystem storage |
| `setBlob(tablename, rowid, column, file)` | — | Write a blob to filesystem storage |
| `delBlob(tablename, rowid, column)` | — | Delete a blob from filesystem storage |

### Configuration

| Method | Returns | Description |
|---|---|---|
| `manage_changeProperties(REQUEST)` | redirect | Save connection_id, charset, table_filter, model |
| `manage_changeConfiguration(REQUEST)` | redirect | Full table/column model CRUD |

## FK-Stereotypes: GUI-Elements for Related Tables

The ZMS-SQLDB-Configurator provides a No-Code-GUI that interconnects related tables
as one configurable relation layer in the same editor.
Through stereotypes, ZMS can map single FKs, n:m links, n-ary combinations, and
full child-record grids into one coherent GUI workflow, including lazy loading and
automatic intersection-target resolution.

- Prefer `Select` for single FK
- Prefer `Multiselect` for one target domain (set of values)
- Prefer `Multi-Multiselect` for n-ary combinations across multiple target domains
- Prefer `Details` for child-record collections with dedicated columns and CRUD


### Select

Use `fk` when one row references exactly one row in another table.

- Typical relation: many-to-one (`n:1`) from source table to lookup table
- GUI behavior: single dropdown or lazy picker (for large lookup tables)
- Best for: master-data references such as `employee`, `category`, `status`
- Efficient when: users choose one value from a bounded or searchable list

Example shape:

```sql
main.employee_id -> employees.employeeid
```

### Multiselect

Use `multiselect` when one row can be linked to multiple rows of one target domain.

- Typical relation: many-to-many (`n:m`) between source and one target table
- Storage variants:
- Intersection table mode: recommended for normalized schemas
- MySQL-Set mode: legacy/string-set style storage
- GUI behavior: multi-select list with add/remove controls; optional lazy loading
- Best for: tags, categories, features, permissions
- Efficient when: one source row needs an arbitrary set of values from one target table

Example shape (intersection mode):

```sql
article_tags(article_id, tag_id)
```

### Multi-Multiselect

Use `multimultiselect` for composite relation rows where each entry is a combination
of multiple foreign keys.

- Typical relation: one source row to many relation rows (`1:n`), each relation row
  contains multiple FK dimensions
- Data model: one relation table with parent FK plus additional FK columns
- GUI behavior: users build one combination row at a time (dimension A + B + C),
  add it with `+`, and maintain a selected combinations list
- Best for: matrix-like assignments such as `employee x role x project` or
  `customer x channel x language`
- Efficient when: the business object is the combination itself, not independent
  single selections

Example shape:

```sql
assignment(main_id, employee_id, role_id, project_id)
```

### Details

Use `details` when a parent record should manage a related child record set directly
inside the same edit context.

- Typical relation: one-to-many (`1:n`) from parent table to detail table
- Also supports: intersection-table based detail relations
- Data model: `details.tablename` points to the related table and `details.fk`
  references the parent key column in that table
- GUI behavior: renders an AJAX-loaded details grid below the main form with
  list, paging, and insert/update/delete actions
- Best for: line items, subordinate rows, translations, and other related rows
  that have their own attributes
- Efficient when: related records have their own lifecycle and columns, so a
  simple select or multiselect control is not sufficient

Example shape:

```sql
orders(order_id, customer_id, order_date)
order_items(item_id, order_id, product_id, qty, unit_price)
```


## Tips

- Use **SQLAlchemy** introspection for best results — it provides the most
  accurate schema detection across database backends.
- Define a **Column Model** to customize stereotypes, labels, and FK
  relationships that cannot be auto-detected from the schema.
- For relation stereotypes (`details`, `multiselect`) that reference
  intersection tables, target resolution now follows the non-source FK via
  `getEntityTarget(...)`.
- The **Table Filter** regex is useful to hide system tables or limit
  access to specific tables in multi-schema databases.
- **Blob columns** store files on the filesystem, not in the database —
  ensure the Zope instance has write access to the blob storage path.
- All CRUD operations fire **event hooks** — use `BeforeInsert`,
  `AfterInsert`, etc. to implement custom validation or triggers.
- For ZODB-based tabular data without an external database, use the
  **ZMS Record Set** instead.


# SQL Parameter Sanitization Guide

## Overview

The `sanitize_sqlparam()` function provides a comprehensive solution for safely normalizing and validating request parameters in ZMS, with advanced SQL injection prevention that handles obfuscation and encoding techniques.

## Function Signature

```python
def sanitize_sqlparam(value, param_type=str, allowed_values=None, default=''):
    """
    Sanitize and normalize a request parameter to a given type, preventing SQL injection
    including obfuscated variants.
    """
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `value` | object | N/A | Raw parameter value (str, list, tuple, or None) |
| `param_type` | type | `str` | Expected type (str, int, float, or bool) |
| `allowed_values` | list/tuple | `None` | Optional whitelist of allowed values |
| `default` | object | `''` | Value to return if validation fails |

## Return Value

Returns the normalized value of the specified `param_type`, or `default` if validation fails.

## Features

### 1. **List/Tuple Normalization**
Automatically converts list and tuple parameters to their last element:

```python
# Multi-value parameter (common from HTML form arrays)
qorder = sanitize_sqlparam(['col1', 'col2'])  # Returns: 'col2'
```

### 2. **Advanced Obfuscation Handling**
Prevents SQL injection through multiple encoding/escaping techniques:

#### URL Encoding
```python
# URL-encoded quote (%27)
value = sanitize_sqlparam("col%27; DROP")  # Returns: "col; DROP"

# Double-encoded (%2527)
value = sanitize_sqlparam("col%2527; DROP")  # Returns: "col; DROP"

# Recursive multi-level decoding
value = sanitize_sqlparam("col%252527")  # Handles triple encoding
```

#### HTML Entities
```python
# HTML numeric entity
value = sanitize_sqlparam("col&#39; DROP")  # Returns: "col DROP"

# HTML named entity
value = sanitize_sqlparam("col&apos; DROP")  # Returns: "col DROP"

# Mixed entities
value = sanitize_sqlparam("col&quot;DROP&quot;")  # Returns: "colDROP"
```

#### Escape Sequences
```python
# Hex escape (\xXX)
value = sanitize_sqlparam("col\\x27 DROP")  # Returns: "col DROP"

# Unicode escape (\uXXXX)
value = sanitize_sqlparam("col\\u0027 DROP")  # Returns: "col DROP"

# Octal escape (\XXX)
value = sanitize_sqlparam("col\\047 DROP")  # Returns: "col DROP"

# Backslash escape (\' and \")
value = sanitize_sqlparam("col\\' DROP")  # Returns: "col DROP"
```

#### SQL Comment Removal
```python
# SQL line comments (--)
value = sanitize_sqlparam("col'--comment")  # Returns: "col"

# SQL block comments (/* */)
value = sanitize_sqlparam("col'/*comment*/")  # Returns: "col"

# MySQL comments (#)
value = sanitize_sqlparam("col'#comment")  # Returns: "col"
```

#### Null Byte Injection
```python
# Null byte removal
value = sanitize_sqlparam("col\\x00 data")  # Returns: "col data"
value = sanitize_sqlparam("col\x00 data")  # Returns: "col data"
```

### 3. **SQL Injection Prevention**
Removes single and double quotes to prevent quote-based SQL injection:

```python
# Malicious input
value = sanitize_sqlparam("name'; DROP TABLE users--")
# Returns: "name; DROP TABLE users--" (quotes and comments removed)

# OR injection prevention
value = sanitize_sqlparam("col' OR 1=1")
# Returns: "col OR 1=1" (quote removed, injection neutralized)
```

### 4. **Whitelist Validation**
Validates string values against an allowed set:

```python
# ORDER BY direction validation
direction = sanitize_sqlparam(
    'desc',
    param_type=str,
    allowed_values=('asc', 'desc'),
    default='asc'
)  # Returns: 'desc'

# Invalid value returns default
direction = sanitize_sqlparam(
    'invalid',
    param_type=str,
    allowed_values=('asc', 'desc'),
    default='asc'
)  # Returns: 'asc'

# Works with URL-encoded invalid values
direction = sanitize_sqlparam(
    'invalid%20value',
    param_type=str,
    allowed_values=('asc', 'desc'),
    default='asc'
)  # Returns: 'asc' (after decoding, still invalid)
```

### 5. **Type Conversion**
Automatically converts values to the requested type:

```python
# String parameter
name = sanitize_sqlparam(['John'], param_type=str)  # 'John'

# Integer parameter
page = sanitize_sqlparam('42', param_type=int, default=1)  # 42

# Float parameter
price = sanitize_sqlparam('19.99', param_type=float, default=0.0)  # 19.99

# Boolean parameter
enabled = sanitize_sqlparam('true', param_type=bool, default=False)  # True
```

### 6. **Graceful Fallback**
Returns default value when conversion fails:

```python
# Invalid integer
page = sanitize_sqlparam('not_a_number', param_type=int, default=1)  # 1

# None value
name = sanitize_sqlparam(None, param_type=str, default='Anonymous')  # 'Anonymous'

# Empty string
name = sanitize_sqlparam('', param_type=str, default='Anonymous')  # 'Anonymous'
```

### 7. **Whitespace Normalization**
Handles various whitespace obfuscation techniques:

```python
# Tabs and newlines
value = sanitize_sqlparam("col\t' DROP\n")  # Returns: "col DROP"

# Multiple spaces
value = sanitize_sqlparam("col   '   DROP")  # Returns: "col DROP"

# Leading/trailing whitespace
value = sanitize_sqlparam("  data  ")  # Returns: "data"
```

## Usage Examples

### Example 1: ORDER BY Clause (Original Use Case)

**Before** (vulnerable pattern):
```python
qorder = REQUEST.get('qorder', '')
qorderdir = REQUEST.get('qorderdir', 'asc')
# Ensure qorder and qorderdir are single values, not lists.
qorder = isinstance(qorder, (list, tuple)) and list(qorder)[-1] or ( isinstance(qorder,str) and qorder or '' )
qorderdir = isinstance(qorderdir, (list, tuple)) and list(qorderdir)[-1] or ( isinstance(qorderdir,str) and qorderdir or 'asc' )
qorderdir = 'desc' if str(qorderdir).strip().lower() == 'desc' else 'asc'
```

**After** (safe and clean):
```python
qorder = sanitize_sqlparam(
    REQUEST.get('qorder', ''),
    param_type=str,
    default=''
)
qorderdir = sanitize_sqlparam(
    REQUEST.get('qorderdir', 'asc'),
    param_type=str,
    allowed_values=('asc', 'desc'),
    default='asc'
)
```

### Example 2: Pagination Parameters

```python
page = sanitize_sqlparam(
    REQUEST.get('page', '1'),
    param_type=int,
    default=1
)
page_size = sanitize_sqlparam(
    REQUEST.get('page_size', '50'),
    param_type=int,
    default=50
)
```

### Example 3: Filter Parameters

```python
# Ensure filter value is string without quotes
filter_value = sanitize_sqlparam(
    REQUEST.get('filter'),
    param_type=str,
    default=''
)

# Ensure column name is in allowed list
column = sanitize_sqlparam(
    REQUEST.get('column'),
    param_type=str,
    allowed_values=allowed_column_names,
    default=allowed_column_names[0]
)
```

### Example 4: Boolean Flags

```python
# Show archived items?
include_archived = sanitize_sqlparam(
    REQUEST.get('include_archived', 'false'),
    param_type=bool,
    default=False
)
```

## Security Considerations

### ✓ What This Function PROTECTS Against

1. **Quote-based SQL Injection** (direct and obfuscated)
   - Direct: `col'; DROP TABLE`
   - URL-encoded: `col%27; DROP TABLE`
   - HTML-encoded: `col&#39; DROP TABLE`
   - Escape sequences: `col\x27; DROP TABLE`, `col\u0027; DROP TABLE`

2. **Comment-based SQL Injection**
   - Line comments: `col'--comment`
   - Block comments: `col'/* comment */`
   - MySQL comments: `col'#comment`

3. **Null Byte Injection**
   - String truncation: `col\x00 data` → `col data`

4. **Type Confusion Attacks**
   - Ensures values are converted to expected type
   - Prevents type juggling vulnerabilities

5. **Unexpected List Values**
   - Normalizes multi-value parameters to single values
   - Takes last value (safer than first)

6. **Double/Recursive Encoding**
   - URL decoding with multiple passes (up to 10 iterations)
   - Catches double-encoded attacks: `col%2527` → `col%27` → `col'`

7. **Whitespace Obfuscation**
   - Normalizes tabs, newlines, multiple spaces
   - Strips leading/trailing whitespace

8. **Missing/Invalid Parameters**
   - Provides safe defaults for all error conditions

### ⚠️ What This Function Does NOT Protect Against

1. **Column Name Injection (Identifiers)**
   - Solution: Use `allowed_values` parameter with whitelist
   ```python
   column = sanitize_sqlparam(
       REQUEST.get('column'),
       param_type=str,
       allowed_values=safe_column_names,  # Whitelist!
       default='id'
   )
   ```

2. **Numeric Out-of-Bounds Attacks**
   - Solution: Add range validation after sanitization
   ```python
   limit = sanitize_sqlparam(REQUEST.get('limit', '10'), param_type=int, default=10)
   if limit < 1 or limit > 100:
       limit = 10  # Force safe default
   ```

3. **Business Logic Errors**
   - Function validates format, not business logic
   - Solution: Add application-level validation

4. **Database-Specific Escaping**
   - Function removes quotes rather than escaping them
   - Solution: Use parameterized queries instead of string concatenation

### Best Practices

1. **Always use parameterized queries** when possible (preferred over sanitization)
   ```python
   # BETTER: Parameterized query
   db.query("SELECT * FROM users WHERE id = ?", [user_id])
   
   # ACCEPTABLE: With sanitization
   user_id = sanitize_sqlparam(REQUEST.get('id'), param_type=int, default=0)
   db.query(f"SELECT * FROM users WHERE id = {user_id}")
   ```

2. **Combine with `allowed_values`** for identifiers like column names
   ```python
   qorder = sanitize_sqlparam(
       REQUEST.get('qorder'),
       param_type=str,
       allowed_values=['id', 'name', 'created_at'],
       default='id'
   )
   ```

3. **Validate ranges** for numeric parameters after sanitization
   ```python
   page = sanitize_sqlparam(REQUEST.get('page', '1'), param_type=int, default=1)
   if page < 1:
       page = 1
   ```

4. **Document expected types** in API specifications
   ```python
   """
   @param sort_order: Sort direction (asc or desc)
   @param sort_column: Column name (must be from allowed list)
   @param limit: Result limit (1-1000)
   """
   ```

5. **Log suspicious input** when defaults are returned
   ```python
   value = sanitize_sqlparam(REQUEST.get('param'), ...)
   if value == default:
       logger.warning(f"Suspicious parameter value rejected: {REQUEST.get('param')}")
   ```

6. **Test with obfuscated payloads** during security audits
   ```
   col%27; DROP TABLE
   col&#39; DROP TABLE
   col\x27; DROP TABLE
   col%2527; DROP TABLE
   col'--comment
   col/**/DROP
   ```

## Migration Guide

To migrate existing code to use `sanitize_sqlparam()`:

### Step 1: Identify Parameter Usage
Search for REQUEST parameter access patterns:
```python
value = REQUEST.get('param_name')
```

### Step 2: Determine Type and Constraints
```python
# String parameter with allowed values?
# Integer parameter with range?
# Boolean flag?
```

### Step 3: Replace with sanitize_sqlparam()
```python
value = sanitize_sqlparam(
    REQUEST.get('param_name', default_value),
    param_type=type,
    allowed_values=None,  # Remove if not applicable
    default=default_value
)
```

## Compatibility

- **Python 2.7+** (uses built-in string operations)
- **Python 3.x** (fully compatible)
- **Zope** (compatible with all versions supporting REQUEST objects)

## Error Handling

The function raises `ValueError` only for invalid `param_type`:

```python
try:
    # This raises ValueError - list is not a supported type
    value = sanitize_sqlparam('test', param_type=list)
except ValueError as e:
    print(f"Invalid parameter type: {e}")
```

All other errors (conversion failures, missing values, etc.) result in returning the `default` value.
