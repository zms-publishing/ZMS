# ZMS CSS/Theming API Reference

This document lists CSS variables, classes, and theming hooks available in ZMS, with examples from the provided themes.

## Core CSS Files
- `style.css`, `web.css`, `custom_zmsdemo.css` (see `zms_theme_basic`)

## Example: Overriding Styles
To override default ZMS styles, add your custom rules to `style.css` or `web.css`:

```css
body {
	background: #f8f9fa;
}
.zms-header {
	color: var(--zms-primary-color, #123456);
}
```

## Using CSS Variables
Themes can define or override CSS variables for colors, fonts, etc.:

```css
:root {
	--zms-primary-color: #0055a5;
	--zms-secondary-color: #e0e0e0;
}
```

## Injecting Custom CSS/JS
Add custom CSS files (e.g., `custom_zmsdemo.css`) and reference them in your templates (`standard_html.zpt`).
Add custom JavaScript in `web.js` or `zmi.js` for theme-specific or admin interface enhancements.
