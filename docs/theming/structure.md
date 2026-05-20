# ZMS Theme Structure

This document describes the folder and file structure required for a ZMS theme package, using the example themes found in `Products/zms/conf/metaobj_manager/com.zms.foundation.theme`.

## Overview
- Folder layout based on real themes (e.g., `zms_theme_basic`, `zms_theme_grayscale`, `zms_theme_minimal`)
- Required and optional files
- Theme registration and activation

## Example Structure (from zms_theme_basic)
```
zms_theme_basic/
  __init__.yaml
  custom_zmsdemo.css
  login_form.zpt
  pageelements.zpt
  standard_html.zpt
  style.css
  web.css
  web.js
  zmi.css
  zmi.js
```

## File Descriptions
- `__init__.yaml`: Theme metadata and configuration
- `style.css`, `web.css`, `custom_zmsdemo.css`: Main CSS files for the theme
- `login_form.zpt`, `standard_html.zpt`, `pageelements.zpt`: Page and block templates
- `web.js`, `zmi.js`: JavaScript for theme and ZMS management interface
- `zmi.css`: CSS for ZMS management interface

## Registration
Themes are registered by placing them in the appropriate directory and ensuring `__init__.yaml` is present. ZMS will detect and list available themes for activation in the admin interface.
