# ZMS Theme Automation & Tools

This document covers scripts and tools for packaging, importing, and exporting ZMS themes, with practical notes for the ZMS theme structure.

## Packaging Themes
- Ensure your theme folder (e.g., `zms_theme_basic/`) contains all required files, including `__init__.yaml`.
- Zip the theme folder for distribution or deployment:

	```sh
	zip -r zms_theme_basic.zip zms_theme_basic/
	```

## Import/Export Tools
- Use the ZMS Repomanager to synchonize the theme data with your (git-) repository
- Use the ZMS admin interface to import/export themes as zip files.
- Place unzipped themes in the appropriate server directory for automatic detection.

## Automation Tips
- Maintain a consistent structure for all themes.
- Use scripts to update version numbers or metadata in `__init__.yaml` across multiple themes.
