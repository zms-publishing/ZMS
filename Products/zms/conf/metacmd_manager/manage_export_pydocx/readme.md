# Word/DOCX Export

## Overview

This script, `manage_export_pydoc.py`, is designed to export content to a Word/DOCX file using the `python-docx` library. It is intended to be used as a ZMS action.

## Prerequisites

- Python 3.x
- `python-docx` library

You can install the required library using pip:

```sh
pip install python-docx
```

## Configuration and Customization

Ensure that the script is configured correctly with the necessary parameters for your specific use case, especially the global variable `docx_tmpl` as filesystem path to the DOCX file that is used as a template:

```py
# Set local path for docx-template
docx_tmpl = open("%s/Extensions/neon.docx"%(os.getenv('INSTANCE_HOME')), "rb")
```
**Hint**: If the export result in an _KeyError_ like  `Error Value: no style with name 'Table-Caption'` the docx-template (which contains the style-definition) can not be located.


You may prefer to export not the committed but the working content, so set the REQUEST-variable:   

```py
# For debugging use preview content
request.set('preview', 'preview')
```

Furthermore You may need to modify the script to fit your data source and desired output format. Some (complex) ZMS content objects may need another template `standard_json_docx` (Python script) to generate a normalized JSON representation of the object's content. The standard content model contains some examples of the script. For further details, please refer to the docstring of 
`manage_export_pydocx.apply_standard_json_docx()`.
