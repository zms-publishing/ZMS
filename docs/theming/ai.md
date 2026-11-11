# AI/Automation Hints for ZMS Themes

This document describes conventions and metadata to help AI tools automate theme creation, using examples from the current ZMS theme structure.

## Naming Conventions
- Use lowercase, underscore-separated folder and file names (e.g., `zms_theme_basic`, `standard_html.zpt`).
- Place all theme files in a dedicated folder with a unique name.

## Manifest/Metadata
- Each theme must include an `__init__.yaml` file with metadata such as name, author, version, and description.
- Example `__init__.yaml`:

  ```yaml
  id: zms_theme_basic
  title: Basic Theme
  author: ZMS Team
  version: 1.0.0
  description: A simple starter theme for ZMS.
  ```

## Machine-Readable Descriptors
- Use YAML for theme metadata (`__init__.yaml`).
- Consider adding a `theme.yaml` or similar for additional AI-relevant properties (e.g., color palette, font stack).

## Example Manifest
```yaml
id: zms_theme_custom
title: Custom Theme
author: Your Name
version: 1.0.0
description: A custom theme generated from Figma design.
colors:
  primary: '#123456'
  secondary: '#abcdef'
fonts:
  body: 'Arial, sans-serif'
```
