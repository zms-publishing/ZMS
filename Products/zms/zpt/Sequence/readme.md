# ZMS ID Sequencer

The **ID Sequencer** (`acl_sequence`) is a persistent auto-increment counter
that generates unique numeric IDs for every ZMS content object. Each time a
new node is created anywhere in the content tree, the sequencer advances and
assigns the next available ID.

## Core Concepts

| Concept | Description |
|---|---|
| **Current Value** | The last ID that was assigned. Displayed in the management form and persisted in the ZODB. |
| **Monotonic Increment** | The counter only moves forward — it can never be set to a value lower than the current one, preventing accidental ID collisions. |
| **Global Scope** | A single sequencer instance serves the entire ZMS site (including portal clients). |

## GUI Layout

The management interface is a single form with:

- **Current Value** — an input field showing the current counter value
- **Change** button — manually set the counter to a new value (must be ≥ current)
- **Next** button — advance the counter by one and display the new value

## API Reference

| Method | Returns | Description |
|---|---|---|
| `__init__(value=0)` | — | Initialize the sequencer with a starting value |
| `nextVal()` | `int` | Increment the counter by 1 and return the new value |
| `currVal()` | `int` | Return the current value without incrementing |
| `manage_changeProperties(value)` | — | Set the counter to a new value (enforces ≥ current) |
| `manage_next(REQUEST)` | redirect | Advance the counter and redirect back to the form |

## Tips

- **Never lower the counter** — doing so would risk duplicate IDs and
  broken internal references (`{$<uid>}`).
- The sequencer value is stored in the ZODB, so it survives server restarts
  and is included in ZODB backups.
- When migrating content between ZMS instances, ensure the target sequencer
  value is higher than the maximum ID in the imported data.
