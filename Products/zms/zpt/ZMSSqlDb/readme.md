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
| `getEntityColumn(tablename, columnname)` | `dict` | Full column metadata including FK, blob, multiselect stereotypes |
| `getEntityPK(tablename)` | `str` | Primary key column name for a table |
| `getEntitiesFromSqlAlchemy()` | `list` | Schema introspection via SQLAlchemy |

### CRUD Operations

| Method | Returns | Description |
|---|---|---|
| `recordSet_Insert(tablename, values, REQUEST)` | `dict` | INSERT a row, handle auto-columns, blobs, FK, intersections |
| `recordSet_Update(tablename, rowid, values, REQUEST)` | `dict` | UPDATE a row with diff detection and blob handling |
| `recordSet_Delete(tablename, rowid, REQUEST)` | — | DELETE a row by primary key |

### Query Building

| Method | Returns | Description |
|---|---|---|
| `getEntityRecordHandler(tablename)` | SQL | Build SELECT with JOINs from entity definition |
| `sql_record_init(tablename, REQUEST)` | — | Initialize SQL statement and request context |
| `sql_record_where(tablename, REQUEST)` | SQL | Build WHERE clause from session filters |
| `sql_record_order(tablename, REQUEST)` | SQL | Build ORDER BY clause |

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

## Tips

- Use **SQLAlchemy** introspection for best results — it provides the most
  accurate schema detection across database backends.
- Define a **Column Model** to customize stereotypes, labels, and FK
  relationships that cannot be auto-detected from the schema.
- The **Table Filter** regex is useful to hide system tables or limit
  access to specific tables in multi-schema databases.
- **Blob columns** store files on the filesystem, not in the database —
  ensure the Zope instance has write access to the blob storage path.
- All CRUD operations fire **event hooks** — use `BeforeInsert`,
  `AfterInsert`, etc. to implement custom validation or triggers.
- For ZODB-based tabular data without an external database, use the
  **ZMS Record Set** instead.
