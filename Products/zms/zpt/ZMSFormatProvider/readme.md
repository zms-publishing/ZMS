
# ZMS Format Provider

The **Format Provider** (`ZMSFormatProvider`) manages text and character format definitions used throughout ZMS for rendering content. It controls how text blocks and inline text fragments are wrapped in HTML when displayed — both in the ZMI editing environment and in the published output.

> **Path:** *Login as ZMS Admin → Configuration → Text Formats / Char Formats*

---

## Core Concepts

### Text Formats (Block Formats)

A **text format** defines how a block of text is rendered as HTML. Each ZMS text block (`ZMSTextarea`) carries a `format` attribute that references a text format by id. When the content is displayed, the format determines the wrapping HTML tag, its attributes, and how line breaks within the block are handled.

#### Data Model

| Property | Description |
|---|---|
| **Id** | Unique identifier (e.g. `body`, `headline1`, `pre`, `code`). |
| **Display** | Localized human-readable name shown in the format dropdown (e.g. *"Body text"*, *"Headline 1"*). Supports multiple ZMI languages. |
| **Tag** | The outer HTML element wrapping the entire text block (e.g. `div`, `pre`, `h1`). Leave empty for no wrapper. |
| **Subtag** (Newline-Tag) | The HTML element inserted for each line break within the block. Typical values: `br` (inserts `<br />`), `p` (wraps each line in `<p>…</p>`). Leave empty for no line-break handling. |
| **Attrs** | Additional HTML attributes on the outer tag (e.g. `class="paragraph"`). |
| **Richedit** | If checked, forces the text block to use the WYSIWYG rich-text editor instead of the standard textarea. |
| **Usage** | Controls in which editor modes the format is selectable: *Standard-Editor*, *Richtext-Editor*, or both. |
| **Default** | One format can be marked as default — it is pre-selected when a new text block is created. Falls back to `body` if none is explicitly set. |

#### Rendering Logic

The `ZMSTextformat` class assembles HTML output from these properties:

```
<Tag Attrs>
  <Subtag>Line 1</Subtag>
  <Subtag>Line 2</Subtag>
</Tag>
```

The subtag also supports **nested lists** via tab-indented markup in the source text:
- `\t* item` → `<ul><li>item</li></ul>`
- `\t# item` → `<ol><li>item</li></ol>`
- Multiple levels of tab-indentation produce nested list structures.

#### Section Numbering

Text formats whose id starts with `headline` (e.g. `headline1`, `headline2`) participate in **automatic section numbering**. The `TextFormatObject.getSecNo()` method computes hierarchical section numbers (e.g. *1.2.3*) based on the `levelnfc` attribute of the parent node, prepending them to the rendered text.

---

### Character Formats (Inline Formats)

A **character format** defines an inline markup that can be applied to selected text within a rich-text editor. Character formats render as inline HTML elements wrapping the selection.

#### Data Model

| Property | Description |
|---|---|
| **Id** | Unique identifier (e.g. `bold`, `code`, `highlight`). |
| **Display** | Human-readable name shown in the editor toolbar. |
| **Icon** | CSS icon class for the toolbar button (e.g. `fas fa-bold`, `fas fa-code`). |
| **Tag** | The inline HTML element (e.g. `strong`, `em`, `code`, `span`). |
| **Attrs** | Additional HTML attributes on the tag (e.g. `class="highlight"`, `style="color:red"`). |
| **JavaScript** | Optional JS code executed when the format button is clicked — enables custom editor interactions beyond simple tag wrapping. |

#### Rendered Output

```html
<Tag Attrs>selected text</Tag>
```

For example, a character format with `tag=span` and `attrs=class="sc"` renders:
```html
<span class="sc">selected text</span>
```

---

## API Reference

### Interface: `IZMSFormatProvider`

All format access methods are defined in the `IZMSFormatProvider` interface, implemented by both `ZMSFormatProvider` (local) and `ZMSFormatProviderAcquired` (inheriting from portal master).

#### Text Format Methods

| Method | Returns | Description |
|---|---|---|
| `getTextFormats(REQUEST)` | `list[ZMSTextformat]` | Returns all text formats, sorted by display name. |
| `getTextFormat(id, REQUEST)` | `ZMSTextformat` or `None` | Returns the text format object for the given id. |
| `getTextFormatDefault()` | `str` | Returns the id of the default text format (the one marked as default, or `body` as fallback). |
| `setTextformat(id, newId, newDisplay, newZMILang, newTag, newSubtag, newAttrs, newRichedit, newUsage)` | — | Creates or updates a text format. Pass `None` as `id` to insert a new format. |
| `delTextformat(id)` | — | Deletes the text format with the given id. |
| `setDefaultTextformat(id)` | — | Marks the specified text format as the default. |

#### Character Format Methods

| Method | Returns | Description |
|---|---|---|
| `getCharFormats()` | `list[dict]` | Returns all character formats as a list of dictionaries. |
| `setCharformat(oldId, newId, newIconClazz, newDisplay, newTag, newAttrs, newJS)` | `str` | Creates or updates a character format. Pass `None` as `oldId` to insert. Returns the new id. |
| `delCharformat(id)` | — | Deletes the character format with the given id. |
| `moveCharformat(id, pos)` | — | Moves a character format to the specified position in the list (controls toolbar order). |

### Class: `ZMSTextformat`

The `ZMSTextformat` object represents a single text format definition and provides the rendering API.

| Method | Returns | Description |
|---|---|---|
| `getId()` | `str` | The format's unique identifier. |
| `getDisplay()` | `str` | The localized display name. |
| `getTag()` | `str` | The outer HTML tag name. |
| `getSubTag()` | `str` | The line-break (newline) tag name. |
| `getAttrs()` | `str` | The HTML attribute string for the outer tag. |
| `parseAttrs()` | `list[tuple]` | Parses the attribute string into a list of `(name, value)` tuples. |
| `getRichedit()` | `int` | `1` if the format forces rich-text editing, `0` otherwise. |
| `getUsage()` | `list[str]` | List of editor modes where this format is available (`'standard'`, `'wysiwyg'`). |
| `getStartTag(id=None, clazz=None)` | `str` | Assembles the opening HTML tag with optional `id` and `class` attributes. |
| `getEndTag()` | `str` | Assembles the closing HTML tag. |
| `getHtml()` | `str` | Returns an HTML-escaped preview of the format's structure (used in the GUI). |
| `renderText(context, text, id=None, clazz=None)` | `str` | Renders the given text through this format: wraps in start/end tags, processes line breaks via `br_quote()`, handles nested list syntax. |

### Content-Level Rendering: `renderText()`

On content objects (`ZMSObject` and descendants), the method `renderText(format, key, text, REQUEST)` in `_textformatmanager.py` is the main entry point for rendering text with a format:

1. Looks up the `ZMSTextformat` by the `format` id.
2. Calls `textformat.renderText()` to produce formatted HTML.
3. Invokes the optional custom hook `renderCustomText()` if defined on the object.
4. If `format == 'markdown'`, applies Python `markdown` rendering and resolves `{$uid:...}` references to actual URLs.

---

## GUI Layout

The Format Provider has **two tabs**:

### Text Formats Tab

A table listing all defined text formats with:

| Column | Description |
|---|---|
| **Checkbox** | For bulk selection (delete, export). |
| **Id** | The format identifier. A 👁 (eye) icon indicates *Richedit* mode; otherwise an alignment icon is shown. |
| **Rendered Preview** | A live preview showing how the format wraps its own display name in HTML. |

The default format is highlighted with a blue info row.

Clicking a format id opens a **modal edit dialog** with all properties (Id, Display, Tag, Subtag, Attrs, Usage, Default, Richedit) plus a *Rendered Code* preview.

### Character Formats Tab

A table listing all defined character formats with:

| Column | Description |
|---|---|
| **Checkbox** | For bulk selection (delete, export). |
| **Icon + Id** | The format's toolbar icon and identifier. Formats without an icon show a vertical separator. |
| **Inline Preview** | A rendered HTML preview of the format applied to its display name. |

Clicking a format id opens a **modal edit dialog** with all properties (Id, Display, Icon, Tag, Attrs, JavaScript) plus a *Rendered Code* preview.

### Toolbar (both tabs)

| Button | Description |
|---|---|
| **＋ Insert** | Opens a dialog to create a new format. |
| **✕ Delete** | Deletes all selected formats after confirmation. |
| **⬆ Import** | Imports format definitions from a `.textfmt.xml` or `.charfmt.xml` file, or from a built-in template. |
| **⬇ Export** | Exports selected formats as XML. |

---

## Import / Export

Format definitions can be serialized as XML configuration files:

- **Text formats:** `.textfmt.xml` — key/value pairs with `display` (multilang dict), `tag`, `subtag`, `attrs`, `richedit`, `usage`, `default`.
- **Character formats:** `.charfmt.xml` — flat dicts with `id`, `display`, `icon_clazz`, `tag`, `attrs`, `js`.

These files can be exchanged between ZMS instances and are also version-controlled through the Repository Manager.

---

## Acquisition from Portal Master

In a multi-site setup, a child site can use `ZMSFormatProviderAcquired` instead of a local `ZMSFormatProvider`. The acquired variant delegates all `getTextFormat*()` and `getCharFormats()` calls to the portal master site, providing centralized format management. The GUI for an acquired provider is read-only (no insert/delete/import buttons).

---

## Tips

- **Headline formats and section numbering:** Name formats `headline1`, `headline2`, etc. to enable automatic section numbering based on the parent node's `levelnfc` (level number format code) attribute.
- **Richedit flag:** Use this to force specific formats (e.g. `richtext`) to always open with the WYSIWYG editor, regardless of the user's default editor preference.
- **Character format JavaScript:** The `js` field can contain custom JavaScript for complex editor interactions — e.g. opening a dialog, inserting special markup, or triggering an API call when the toolbar button is clicked.
- **Markdown support:** The special format value `markdown` bypasses ZMSTextformat rendering entirely and uses Python's `markdown` library. UID references (`{$uid:...}`) within markdown text are automatically resolved to ZMS link URLs.
