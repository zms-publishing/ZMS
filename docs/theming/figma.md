# Figma to ZMS Theme Mapping

This document provides guidance for mapping Figma design tokens to ZMS theme variables and assets, with practical examples for integration.

## Exporting from Figma
- Export color palettes and typography as CSS variables or SCSS from Figma (using plugins or manual copy).
- Export images and SVGs for use in the theme's `common/` or asset folders.

## Mapping Table
| Figma Token      | ZMS Variable/CSS/File         |
|------------------|------------------------------|
| Primary Color    | --zms-primary-color (styles/web.css) |
| Secondary Color  | --zms-secondary-color (styles/web.css) |
| Logo Image       | common/logo.png             |
| Heading Font     | font-family in style.css     |
| ...              | ...                          |

## Recommendations
- Use Figma export settings that match web usage (e.g., 1x PNG, SVG for icons).
- Map Figma tokens directly to CSS variables in your theme's CSS files.
- Keep exported assets organized and named consistently with your theme structure.
