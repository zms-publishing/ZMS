# ZMS Logger

The **ZMS Logger** (`ZMSLog`) provides a centralized logging facility for the ZMS application. It wraps Python's standard `logging` module, adds ZMS-specific context (object path and meta-type) to log messages, and exposes the Zope event log through a simple GUI for live inspection.

> **Path:** *Login as ZMS Admin → Zope Management Interface (ZMI) → zms_log*

---

## Core Concepts

### Severity Levels

The ZMS Logger recognizes three severity levels:

| Level | Constant | Description |
|---|---|---|
| **DEBUG** | `logging.DEBUG` | Verbose diagnostic messages. Only logged if DEBUG is enabled in the logger settings. |
| **INFO** | `logging.INFO` | General operational messages (e.g. indexing progress, repository sync, import/export). |
| **ERROR** | `logging.ERROR` | Error messages with full traceback information. |

The **Logged entry types** setting controls which severity levels are actually written to the log. By default, only `ERROR` is enabled. Enabling `DEBUG` and `INFO` generates significantly more output and should be used for troubleshooting only.

### Log Output

Log entries are written to Zope's **event log** file (as configured by the `[handler_eventlog]` section in `zope.ini`). The logger reads this file back for the GUI display.

Each log entry is formatted as:

```
YYYY-MM-DDTHH:MM:SS LEVEL(severity) [meta_id@/physical/path] message
```

The `[meta_id@/physical/path]` prefix is automatically added by the logging convenience functions, providing context about which ZMS object produced the message.

### Copy to Standard-Out

When enabled, log messages are additionally printed to the process's standard output (`stdout`). This is useful during development — e.g. when running Zope in foreground mode — but should typically be disabled in production.

---

## GUI Layout

The ZMS Logger management page shows two sections:

### Settings Form

| Field | Description |
|---|---|
| **Lines back in event log** | Number of lines to read from the end of the event log file for display (default: `100`). |
| **Copy entries to standard-out** | Checkbox to additionally print log messages to `stdout`. |
| **Logged entry types** | Multi-select of severity levels (`DEBUG`, `INFO`, `ERROR`) that the ZMS Logger should capture. |
| **Save Changes** | Persists the settings above. |

### Event Log Viewer

A card displaying the last *N* lines (as configured) from Zope's event log file in a `<pre>` block. This provides a quick way to inspect recent log output without SSH access to the server.

A **⬇ Download** icon in the card header links to the full event log file download via `./getLOG`.

---

## API Reference

### Logging Convenience Functions (`Products.zms.standard`)

These module-level functions are the primary logging API used throughout ZMS code. Each function automatically prefixes the message with `[meta_id@/physical/path]` context and checks whether the corresponding severity level is enabled.

| Function | Severity | Description |
|---|---|---|
| `standard.writeLog(context, info)` | `DEBUG` | Logs debug-level information. Only written if DEBUG is in the logger's `logged_entries`. Returns the info string. |
| `standard.writeBlock(context, info)` | `INFO` | Logs informational messages. Only written if INFO is in `logged_entries`. Returns the info string. |
| `standard.writeError(context, info)` | `ERROR` | Logs error messages. Automatically appends the current exception traceback (`sys.exc_info()`). Returns a formatted `TYPE: value` error string. |
| `standard.writeStdout(context, info)` | — | Writes directly to `stdout` via `print()`. No severity check, no event log. For development only. |

**Usage example (in Python Scripts or product code):**

```python
from Products.zms import standard

# Info-level log
standard.writeBlock(self, '[MyFeature] processing %i items' % count)

# Error-level log (call inside an except block)
try:
    ...
except:
    standard.writeError(self, '[MyFeature] failed to process')
```

### ZMSLog Instance Methods

| Method | Description |
|---|---|
| `LOG(severity, info)` | Core logging method. Writes to the Python `logging.getLogger("ZMS")` logger. If `copy_to_stdout` is enabled, also prints to stdout with a timestamp. |
| `getLOG(REQUEST, RESPONSE)` | Returns the full event log file content as `text/plain` (used by the download link). |
| `hasSeverity(severity)` | Returns `True` if the given severity level (as `logging` constant) is in the configured `logged_entries`. |
| `tail_event_log(linesback=100, returnlist=True)` | Reads the last *N* lines from the event log file. Returns a list of strings (or a single string if `returnlist=False`). |
| `get_log_filename()` | Returns the absolute path to Zope's event log file, determined from the root logger's `FileHandler`. Raises `RuntimeError` if no file handler is configured. |

### Properties

| Property | Type | Default | Description |
|---|---|---|---|
| `copy_to_stdout` | `bool` | `False` | Whether to duplicate log messages to stdout. |
| `logged_entries` | `list[str]` | `['ERROR']` | Active severity levels: any combination of `'DEBUG'`, `'INFO'`, `'ERROR'`. |
| `tail_event_log_linesback` | `int` | `100` | Number of lines shown in the event log viewer. |

---

## Tips

- **Enable INFO temporarily** when debugging ZMSIndex re-indexing, Repository Manager sync, or filter execution — these operations produce detailed INFO-level progress messages.
- **Keep DEBUG disabled in production** — it generates very high log volume and can impact performance.
- **Event log file location** is defined in `zope.ini` under `[handler_eventlog]`. The ZMS Logger reads from that same file. If no file handler is configured, `get_log_filename()` will raise an error.
- **Traceback capture:** `standard.writeError()` must be called inside an `except` block — it calls `sys.exc_info()` to capture the current exception traceback automatically.
