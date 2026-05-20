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
