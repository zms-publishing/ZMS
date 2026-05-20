# ZMS Asset Integration Guide

This document describes how to add and reference images, SVGs, fonts, and other assets in a ZMS theme, using examples from the provided themes.

## Adding Assets
- Place images, SVGs, and other static assets flat into the theme folder. In Zope the files will be placed in a `common/` folder and its subfolders (`img`, `styles` etc., e.g. `zms_theme_basic/common/styles`) according to path syntax of the id-field (e.g. `id: zms_theme_basic/common/styles/web.js`) in the `__init__.yaml`-file.
- Bigger data like fonts and other static assets can be organized in a different named `assets/` as needed and referenced via a Zope FilesystemView-object.

## Referencing Assets
- Reference images in your CSS or templates using relative paths:

  ```css
  .logo {
    background-image: url('common/img/logo.png');
  }
  ```
- In templates, use TAL expressions to generate asset URLs dynamically if needed.

## Best Practices
- Use clear, descriptive names for asset files (e.g., `logo.png`, `background.svg`).
- Optimize images for web (compression, appropriate resolution).
- Keep asset folders organized for maintainability and clarity.
