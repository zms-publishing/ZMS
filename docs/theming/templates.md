# ZMS Template/Markup Guidelines

This document explains how to customize layouts and blocks using ZMS templates, based on the structure of the example themes in `com.zms.foundation.theme`.

## Template Structure

Each ZMS theme typically contains the following template files:

- **standard_html.zpt**: The main HTML page template. Defines the overall page structure, includes CSS/JS, and sets up macros for reusable blocks (e.g., header, footer, navigation).
- **pageelements.zpt**: Contains macros for reusable page elements, such as the table of contents (TOC) and footer. These macros can be included in other templates using the `metal:use-macro` directive.
- **login_form.zpt**: Template for the login form, including form fields and styling.
- Other templates (e.g., `standard_html_header.zpt`, `standard_html_footer.zpt`) may be present for further customization.

Templates use TAL (Template Attribute Language) and METAL (Macro Expansion TAL) for dynamic content and macro definitions.

## Example: Main Template (`standard_html.zpt`)

- Sets up page metadata, loads CSS/JS, and defines variables using `tal:define`.
- Uses macros for common elements (e.g., navigation, footer).
- Example macro usage:

	```xml
	<tal:block metal:use-macro="here/pageelements/macros/toc" />
	<tal:block metal:use-macro="here/pageelements/macros/footer" />
	```

## Customizing Layouts

- To modify the overall layout, edit `standard_html.zpt`.
- To change or extend reusable blocks, edit or add macros in `pageelements.zpt`.
- You can add new macros for custom blocks/widgets and include them in your main template or other templates.

## Adding New Blocks/Widgets

1. **Define a Macro**:  
	 In `pageelements.zpt`, add a new macro using `metal:define-macro`.

	 ```xml
	 <tal:block metal:define-macro="custom_block">
		 <!-- Custom HTML and TAL here -->
	 </tal:block>
	 ```
2. **Use the Macro**:  
	 In your main template or another template, include the macro:

	 ```xml
	 <tal:block metal:use-macro="here/pageelements/macros/custom_block" />
	 ```

## Best Practices

- Keep reusable elements in `pageelements.zpt` for maintainability.
- Use descriptive macro names.
- Leverage TAL for dynamic content and METAL for macro reuse.
- Follow the structure and naming conventions found in the example themes (`zms_theme_basic`, `zms_theme_grayscale`, `zms_theme_minimal`).
