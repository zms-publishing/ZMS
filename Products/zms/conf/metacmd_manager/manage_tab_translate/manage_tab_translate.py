## Script (Python) "manage_tab_translate"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=*** DO NOT DELETE OR MODIFY ***
##


#################################################
# Helper Functions
#################################################
# 1. renderHtml
# 2. renderEditMode
# 3. renderViewMode
# 4. renderGoogleTranslate
# 5. renderStyles
# 6. renderScripts
# 7. set_language_options

# ----------------------------------------
# Basic HTML rendering function
# ----------------------------------------
def renderHtml(zmscontext, request, SESSION, fmName='form0'):
	"""Basic HTML rendering function for the translation interface"""
	
	# Set request defaults
	request.set('lang', 'ger')
	request.set('preview', 'preview')
	request.set('fmName', fmName)
	
	# Get GUI mode for translation (edit or view)
	translate_mode = request.get('translate_mode', SESSION.get('translate_mode', 'edit'))
	SESSION.set('translate_mode', translate_mode)
	
	# Set language options
	set_language_options(zmscontext, request, SESSION)

	html = []
	html.append('<!DOCTYPE html>')
	html.append('<html lang="en">')
	html.append(zmscontext.zmi_html_head(zmscontext, request))
	html.append('<body id="manage_translate" class="%s">'%(' '.join(['zmi',request['lang'],'cleanup_recursive', zmscontext.meta_id])))
	html.append(zmscontext.zmi_body_header(zmscontext,request))
	html.append('<div id="zmi-tab">')
	html.append(zmscontext.zmi_breadcrumbs(zmscontext,request))
	html.append('<form class="card form-horizontal translate-forms" action="manage_changeProperties" method="post" enctype="multipart/form-data">')
	html.append('<input type="hidden" name="preview" value="preview"/>')
	html.append('<input type="hidden" id="translate_lang" name="lang" value="%s"/>' % request.get('lang2'))
	html.append('<legend>')
	html.append('<div class="d-inline-block">')
	
	# Create debug info tooltip content
	debug_info = 'REQUEST.lang1: %s | REQUEST.lang2: %s | SESSION.lang1: %s | SESSION.lang2: %s | SESSION.translate_mode: %s' % (
		request.get('lang1', ''),
		request.get('lang2', ''),
		SESSION.get('lang1', ''),
		SESSION.get('lang2', ''),
		SESSION.get('translate_mode', '')
	)
	
	html.append('Translate Content of Node: <code style="font-size:100%%" data-toggle="tooltip" data-placement="bottom" title="%s">%s [%s]</code>'%(debug_info, zmscontext.meta_id, zmscontext.id))
	html.append('</div>')

	# Translate mode toggle buttons
	html.append('<div class="translate_mode-toggle btn-group btn-group-sm float-right" role="group">')
	view_active = ' active" disabled="disabled' if translate_mode == 'view' else '" onclick="switch_translate_mode(\'view\')'
	edit_active = ' active" disabled="disabled' if translate_mode == 'edit' else '" onclick="switch_translate_mode(\'edit\')'
	html.append('<button type="button" title="View Mode: Rendered HTML in two languages side-by-side" class="btn btn-secondary py-0 px-3%s">VIEW</button>' % view_active)
	html.append('<button type="button" title="Edit Mode: Edit HTML-form of two languages side-by-side" class="btn btn-secondary py-0 px-3%s">EDIT</button>' % edit_active)
	html.append('</div>')

	html.append('</legend>')

	html.append('<div id="manage_tab_translate_body" class="card-body p-0 m-0">')

	# Render based on view mode
	if translate_mode == 'view':
		html.append(renderViewMode(zmscontext, request))
	else:
		html.append(renderEditMode(zmscontext, request))
	
	html.append('</div>')
	
	# Save buttons (only in edit mode)
	if translate_mode == 'edit':
		html.append('''
			<div class="controls save text-right p-3">
				<button type="submit" name="btn" class="btn btn-primary" value="BTN_SAVE">%s</button>
				<button type="button" class="btn btn-secondary" onclick="window.location.reload();" value="BTN_CANCEL">%s</button>
			</div>'''%(zmscontext.getZMILangStr('BTN_SAVE'), zmscontext.getZMILangStr('BTN_CANCEL')))
	
	html.append('</form>')
	html.append('</div>')
	
	# Google Translate Element
	html.append(renderGoogleTranslate())
	
	# Add styles and scripts
	html.append(renderStyles())
	html.append(renderScripts())
	
	html.append('</body>')
	html.append('</html>')
	
	return '\n'.join(html)


# ----------------------------------------
# Render edit mode with form fields
# ----------------------------------------
def renderEditMode(zmscontext, request):
	"""Render edit mode with form fields"""
	html = []
	
	# Language selector header
	html.append('<table class="language-selector-header"><tr class="notranslate">')
	for si in ['left', 'right']:
		lang_req_key = 'lang1' if si == 'left' else 'lang2'
		
		html.append('<td class="lang-select-cell zmi-translate-%s" width="50%%">' %(si))
		
		# Language selector
		lang_options_html = []
		for opt in request.get(lang_req_key + '_options'):
			selected = ' selected="selected"' if opt[0] == request.get(lang_req_key) else ''
			lang_options_html.append('<option value="%s"%s>%s</option>' % (opt[0], selected, opt[1]['label']))
		
		html.append('<select class="form-control form-control-sm d-inline w-auto lang" name="%s" onchange="switchLanguage(\'%s\', this.value);">' % (lang_req_key, lang_req_key))
		html.extend(lang_options_html)
		html.append('</select>')
		
		# Add translate button on right column
		if si == 'right':
			html.append('''<button type="button" 
				class="btn btn-sm btn-success form-control-sm w-auto m-1" 
				onclick="triggerAutoTranslate()" 
				title="Auto-translate from %s to %s">Auto-Translate</button>''' % (
					request.get('lang1'), 
					request.get('lang2'))
			)

		html.append('</td>')
	html.append('</tr></table>')
	
	# Render property forms side by side	
	html.append('<table class="properties-table" width="100%">')
	
	# Get object attributes
	objAttrs = zmscontext.getObjAttrs()
	
	# Technical attributes to exclude from translation interface
	technical_prefixes = ('change_', 'work_', 'attr_active_', 'created_', 'modified_')
	technical_attrs = ('uid', 'version', 'preview')
	
	for objAttrId in objAttrs:
		metaObjAttr = zmscontext.getObjAttr(objAttrId)
		
		# Skip technical/system attributes
		if objAttrId.startswith(technical_prefixes) or objAttrId in technical_attrs:
			continue
		
		# Check if attribute is multilang
		is_multilang = metaObjAttr.get('multilang') in [1, True]
		
		if is_multilang:
			html.append('<tr class="form-group-row">')
			
			# Render for both languages
			for si in ['left', 'right']:
				lang = request.get('lang1' if si == 'left' else 'lang2')
				request.set('lang', lang)
				
				elName = zmscontext.getObjAttrName(metaObjAttr, lang)
				elLabel = '%s [%s_%s]' % (zmscontext.getObjAttrLabel(metaObjAttr), metaObjAttr['id'], lang)
				is_mandatory = metaObjAttr.get('mandatory')
				
				html.append('<td class="form-group-cell zmi-translate-block zmi-translate-%s" width="50%%" valign="top">' % si)
				html.append('<div class="form-group row" id="tr_%s">' % elName)
				html.append('<label for="%s" class="col-sm-3 control-label%s">' % (elName, ' mandatory' if is_mandatory else ''))
				html.append('<span>%s</span>' % elLabel)
				html.append('</label>')
				html.append('<div class="col-sm-9">')
				
				# Render the input field
				try:
					input_html = zmscontext.getObjInput(metaObjAttr['id'], request)
					html.append(input_html)
				except Exception as e:
					html.append('<span class="text-danger">Error rendering field: %s</span>' % str(e))
				
				html.append('</div>')
				html.append('</div>')
				html.append('</td>')
			
			html.append('</tr>')
	
	html.append('</table>')
	
	return '\n'.join(html)

# ----------------------------------------
# Render view mode with rendered content
# ----------------------------------------
def renderViewMode(zmscontext, request):
	"""Render view mode with rendered content side-by-side"""
	html = []
	
	# Language selector header
	html.append('<table class="language-selector-header"><tr class="notranslate">')
	for si in ['left', 'right']:
		lang_req_key = 'lang1' if si == 'left' else 'lang2'
		
		html.append('<td class="lang-select-cell zmi-translate-%s" width="50%%">' %(si))
		
		# Language selector
		lang_options_html = []
		for opt in request.get(lang_req_key + '_options'):
			selected = ' selected="selected"' if opt[0] == request.get(lang_req_key) else ''
			lang_options_html.append('<option value="%s"%s>%s</option>' % (opt[0], selected, opt[1]['label']))
		
		html.append('<select class="form-control form-control-sm d-inline w-auto lang" name="%s" onchange="switchLanguage(\'%s\', this.value);">' % (lang_req_key, lang_req_key))
		html.extend(lang_options_html)
		html.append('</select>')
		html.append('</td>')
	html.append('</tr></table>')
	
	# Content table
	html.append('<table class="content-view-table" width="100%">')
	
	# Get child nodes for display
	try:
		childNodes = [x for x in zmscontext.getObjChildren('e', request) if x.isPageElement()]
	except:
		childNodes = []
	
	# Render current node row
	html.append('<tr class="clickable-row" title="Edit translation %s" valign="top">' % zmscontext.absolute_url())
	
	# Render left and right columns (current node)
	for si in ['left', 'right']:
		lang_req_key = 'lang1' if si == 'left' else 'lang2'
		notranslate_class = 'notranslate' if si == 'left' else 'translate'
		
		html.append('<td class="zmi-translate-%s %s translate_mode-cell" width="50%%">' % (si, notranslate_class))
		
		# Set language for content rendering
		request.set('lang', request.get(lang_req_key))
		
		html.append('<div id="%s" class="zmi-translate-element">' % zmscontext.id)
		html.append('<div class="zmiRenderShort" id="%s_%s">' % (zmscontext.id, request.get('lang')))
		
		# Render content based on meta_id
		try:
			if zmscontext.meta_id not in ['ZMSDocument', 'ZMSFolder', 'ZMS']:
				html.append(zmscontext.getBodyContent(request))
			else:
				html.append('<h1>%s</h1>' % zmscontext.getTitle(request))
				desc = zmscontext.getDCDescription(request).replace('\n', '<br />')
				html.append('<p class="description">%s</p>' % desc)
		except Exception as e:
			html.append('<p class="text-muted">No rendered content available</p>')
		
		html.append('</div>')
		html.append('</div>')
		html.append('</td>')
	
	html.append('</tr>')
	
	# Render child nodes
	for childNode in childNodes:
		# Prepare translate URL for child node with edit mode
		translate_url = '%s/manage_tab_translate' % (childNode.absolute_url())
		
		# Check if node is inactive
		inactive_class = ''
		try:
			request.set('lang', request.get('lang1_bk'))
			if not childNode.isActive(request):
				inactive_class = ' inactive-node'
		except:
			pass
		
		html.append('<tr class="clickable-row%s" data-url="%s" title="Edit translation %s" valign="top">' % (inactive_class, translate_url, childNode.absolute_url()))
		
		for si in ['left', 'right']:
			lang_req_key = 'lang1' if si == 'left' else 'lang2'
			notranslate_class = 'notranslate' if si == 'left' else 'translate'
			
			request.set('lang', request.get(lang_req_key + '_bk'))
			
			html.append('<td class="zmi-translate-%s %s translate_mode-cell">' % (si, notranslate_class))
			try:
				html.append('<div class="zmiRenderShort" id="%s_%s">%s</div>' % (childNode.id, request.get('lang'), childNode.renderShort(request)))
			except:
				html.append('<div class="zmiRenderShort" id="%s_%s"><p class="text-muted">Content not available</p></div>' % (childNode.id, request.get('lang')))
			html.append('</td>')
		
		html.append('</tr>')
	
	html.append('</table>')
	
	return '\n'.join(html)


# ----------------------------------------
# Render Google Translate widget
# ----------------------------------------
def renderGoogleTranslate():
	"""Render Google Translate widget HTML and JavaScript"""
	return '''
		<!-- Google Translate Element -->
		<div id="google_translate_element" class="d-block px-3" style="margin-top: 16px;"></div>
		<script>
		//<!--
		var langmap = {
			"ger": "de",    // German
			"eng": "en",    // English
			"fra": "fr",    // French
			"ita": "it",    // Italian
			"spa": "es",    // Spanish
			"rus": "ru",    // Russian
			"tur": "tr"     // Turkish
			// add more as needed
		};
		
		// Grab your source and target language values
		var lang1 = $('select[name="lang1"]').val();
		var lang2 = $('select[name="lang2"]').val();
		var sourceLang = langmap[lang1] || 'en';
		var targetLang = langmap[lang2] || 'en';

		// Initialize Google Translate element
		function googleTranslateElementInit() {
			new google.translate.TranslateElement({
				pageLanguage: sourceLang,
				includedLanguages: targetLang,
				layout: google.translate.TranslateElement.InlineLayout.SIMPLE,
				autoDisplay: false
			}, 'google_translate_element');
		}

		// Function to translate text using Google Translate API (client-side)
		function translateText(text, callback) {
			if (!text || text.trim() === '') {
				callback(text);
				return;
			}
			
			// Use Google Translate free endpoint
			var url = 'https://translate.googleapis.com/translate_a/single?client=gtx&sl=' + 
					sourceLang + '&tl=' + targetLang + '&dt=t&q=' + encodeURIComponent(text);
			
			fetch(url)
				.then(response => response.json())
				.then(data => {
					if (data && data[0]) {
						var translatedText = data[0].map(item => item[0]).join('');
						callback(translatedText);
					} else {
						callback(text);
					}
				})
				.catch(error => {
					console.error('Translation error:', error);
					callback(text); // Return original text on error
				});
		}

		// Copy and translate content from left to right column
		function translateAndCopy() {
			var totalFields = 0;
			var processedFields = 0;
			
			// Count total fields to process
			$('.form-group-row').each(function() {
				var $row = $(this);
				var $leftCell = $row.find('.zmi-translate-left');
				var $rightCell = $row.find('.zmi-translate-right');
				
				if ($leftCell.length && $rightCell.length) {
					var $leftInput = $leftCell.find('input[type="text"], textarea');
					var $rightInput = $rightCell.find('input[type="text"], textarea');
					
					if ($leftInput.length && $rightInput.length) {
						totalFields++;
					}
				}
			});
			
			if (totalFields === 0) {
				alert('No translatable fields found.');
				return;
			}
			
			// Show progress indicator
			$('body').append('<div id="translate-progress" style="position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);background:white;padding:20px;border:2px solid #007bff;border-radius:5px;z-index:10000;"><i class="fas fa-spinner fa-spin"></i> Translating... <span id="progress-counter">0/' + totalFields + '</span></div>');
			
			// Process each row
			$('.form-group-row').each(function() {
				var $row = $(this);
				var $leftCell = $row.find('.zmi-translate-block.zmi-translate-left');
				var $rightCell = $row.find('.zmi-translate-block.zmi-translate-right');
				
				if ($leftCell.length && $rightCell.length) {
					// Find input fields
					var $leftInput = $leftCell.find('input[type="text"], textarea');
					var $rightInput = $rightCell.find('input[type="text"], textarea');
					
					if ($leftInput.length && $rightInput.length) {
						var sourceText = $leftInput.val();
						
						if (sourceText && sourceText.trim() !== '') {
							// Translate and copy
							translateText(sourceText, function(translatedText) {
								$rightInput.val(translatedText);
								$rightInput.css('background-color', '#ffffcc'); // Highlight changed field
								
								processedFields++;
								$('#progress-counter').text(processedFields + '/' + totalFields);
								
								if (processedFields >= totalFields) {
									setTimeout(function() {
										$('#translate-progress').remove();
										alert('Translation completed for ' + processedFields + ' field(s)!');
									}, 500);
								}
							});
						} else {
							processedFields++;
							$('#progress-counter').text(processedFields + '/' + totalFields);
							
							if (processedFields >= totalFields) {
								setTimeout(function() {
									$('#translate-progress').remove();
									alert('Translation completed for ' + processedFields + ' field(s)!');
								}, 500);
							}
						}
					}
				}
			});
		}

		// Manual translation trigger
		window.triggerAutoTranslate = function() {
			if (confirm('This will copy and translate content from ' + lang1 + ' to ' + lang2 + '. Continue?')) {
				translateAndCopy();
			}
		};

		// Once the widget is ready
		$(document).ready(function() {
			// Clean up labels by removing language codes
			$('.zmi-translate-block label span').each(function() {
				try {
					let currentText = $(this).text(); 
					let newText = currentText.replace(/\\[.*?\\]/g, ''); 
					$(this).text(newText); 
				} catch (error) {
					console.log(error);
				}
			});
			setTimeout(function() {
				var $combo = $('#google_translate_element select.goog-te-combo');
				if ($combo.length) {
					$combo.val(targetLang);
					$combo.trigger('change');
				}
				// Reset RTE fields to apply translation
				$('.form-richtext-wysiwyg > .col-sm-12 > .btn-group > span.btn').click()
			}, 1000);
		});
		//-->
		</script>
		<script src="https://translate.google.com/translate_a/element.js?cb=googleTranslateElementInit"></script>
		<!-- /Google Translate Element -->
	'''

# ----------------------------------------
# Render CSS styles
# ----------------------------------------
def renderStyles():
	"""Render CSS styles"""
	return '''
		<style>
			.zmi #zmi-tab {
				padding-bottom: 0 !important;
			}
			/* View mode toggle */
			.translate_mode-toggle {
				margin: -.1rem -.85rem 0 0;
			}
			.translate_mode-toggle .btn.active {
				cursor: default;
			}
			.translate_mode-toggle:hover:has(.btn:not(.active):hover) .btn.active {
				background-color: white;
				color:#545b62;
				transition: 1s;
			}
			
			/* View mode content table */
			.content-view-table {
				border-collapse: collapse;
			}
			.content-view-table .translate_mode-cell {
				padding: 4px;
				vertical-align: top;
			}
			
			/* Clickable rows */
			.clickable-row {
				cursor: pointer;
				transition: background-color 0.2s ease, box-shadow 0.2s ease;
			}
			.clickable-row:hover {
				background-color: #d1e5f6;
				box-shadow: inset 0 0 0 2px rgba(0, 123, 255, 0.5);
			}
			.clickable-row:hover td {
				background-color: transparent !important;
			}
			.clickable-row.inactive-node {
				background-color: #e9ecef;
				opacity: 0.7;
			}
			/* Disable links and interactive elements in view mode cells */
			.translate_mode-cell a,
			.translate_mode-cell button:not(.lang):not([onclick*="switchLanguage"]) {
				pointer-events: none;
				cursor: default;
			}

			/* Rendered content */
			.zmiRenderShort {
				margin-top: 1.5em;
				padding: 0.5rem;
			}
			.zmi figure img {
				max-width: 100%;
				height: auto;
			}
			.zmi header > nav {
				opacity:0.75;
			}
			.zmi header ol *,
			.zmi header ol li:before {
				color:white !important;
			}
			.zmi header ol {
				padding-left:0 !important;
			}
			.zmi .debug_info {
				position: absolute;
				right: 0;
				top: 0;
				z-index: 1000;
			}
			.zmi .debug_info .code {
				display:none;
				background: #ffffff;
				color: black;
				margin: 1.65rem;
				padding: 1rem;
				font-family: courier;
				border: 1px solid #354f67;
				box-shadow: 0 6px 12px rgba(0,0,0,.175);
				font-weight: bold;
			}
			.zmi .debug_info:hover .code {
				display: block;
			}
			.zmi .debug_info i {
				position: absolute;
				right: 0;
				top: 0;
				padding: .75rem;
			}
			/* Language Selector Header */
			.language-selector-header {
				width: 100%;
				border-collapse: collapse;
				margin:0;
				border-bottom: 1px solid #dee2e6;
			}
			.lang-select-cell {
				padding: 0.5rem;
				text-align: left;
			}
			.lang-select-cell select.lang {
				display: inline-block;
				width: auto;
				min-width: 9rem;
			}
			.lang-select-cell.zmi-translate-left {
				border-right: 1px solid #dee2e6;
				text-align: right;
			}
			.zmi-translate-element-id {
				display: inline-block;
				float: left;
				padding: .5rem 1rem;
				font-weight: bold;
			}
			.zmi-translate-element-id a {
				color: #007bff !important;
				text-decoration: none;
			}
			.zmi-translate-element-id a:hover {
				text-decoration: underline;
			}
			.lang-select-cell .btn {
				vertical-align: middle;
			}
			.temp-translate,
			.temp-translate-rich {
				display: none !important;
				visibility: hidden !important;
				position: absolute;
				left: -9999px;
			}
			
			/* Translation Forms */
			.translate-forms {
				margin: 0;
			}
			.properties-table {
				width: 100%;
				border-collapse: collapse;
			}
			.form-group-row {
				border-bottom: 1px solid #dee2e6;
			}
			.form-group-cell {
				padding: 1rem;
				vertical-align: top;
			}
			.form-group-cell.zmi-translate-left {
				border-right: 1px solid #dee2e6;
			}

			/* Form Groups */
			.form-group-cell .form-group {
				margin-bottom: 0;
			}
			.form-group-cell .control-label {
				font-weight: 600;
				font-size: 0.9rem;
			}
			.form-group-cell {
				font-weight: 600;
				font-size: 0.9rem;
			}
			.zmi-translate-right {
				background-color: aliceblue;
			}
			.form-group-cell .control-label.mandatory::after {
				content: " *";
				color: red;
			}
			
			/* Input Fields */
			.input-group {
				flex-wrap: nowrap !important;
			}
			.form-group-cell input[type="text"],
			.form-group-cell textarea,
			.form-group-cell select {
				width: 100%;
			}
			.form-group-cell textarea {
				min-height: 100px;
			}

			/* Rich Text Editors */
			.form-group-cell .zmi-richtext {
				min-height: 200px;
			}
			.form-group-cell .form-richtext-wysiwyg .col-sm-12 .btn-group.pull-right .btn {
				display: block !important;
			}
			.zmi-translate-block .inlinelinks {
				flex: 0 0 100%;
				max-width: 100%;
				margin: .5rem -15px 1rem;
				font-size: 80%;
				font-family: SFMono-Regular,Menlo,Monaco,Consolas,"Liberation Mono","Courier New",monospace;
				display: flex;
				-ms-flex-wrap: wrap;
				flex-wrap: wrap;
				position: relative;
				width: 100%;
				min-height: 1px;
				padding-right: 15px;
				padding-left: 15px;
				font-weight: normal;
			}
			.zmi-translate-block .inlinelinks:before {
				content:"\\f0c1";
				font-family:'Font Awesome 5 Free';
				font-weight:900;
				margin-right:.3rem;
				color:#999;
			}
			/* Google Translate Element */
			#google_translate_element{
				float: right;
				margin: 0.3em;
			}

			// Switch view mode
			.skiptranslate iframe {
				min-height: 2.7rem;
				background: #fff;
				padding-top: .15rem;
			}
			[style*="background-color: rgb(255, 255, 204)"] {
				background-color: #ffeef0 !important;
			}
			/* Responsive adjustments */
			@media (min-width: 1200px) {
				.form-group-cell.zmi-translate-right .control-label {
					display:none
				}
			}
			@media (max-width: 1200px) {
				.form-group-cell .col-sm-3 {
					flex: 0 0 100%;
					max-width: 100%;
				}
				.form-group-cell .col-sm-9 {
					flex: 0 0 100%;
					max-width: 100%;
				}
			}
		</style>
	'''

# ----------------------------------------
# Render JavaScript code

def renderScripts():
	"""Render JavaScript code"""
	return '''
		<script>
			// Switch language and reload page
			function switchLanguage(langKey, langValue) {
				const url = new URL(window.location);
				url.searchParams.set(langKey, langValue);
				window.location.href = url.toString();
			}

			function switch_translate_mode(mode) {
				const url = new URL(window.location);
				url.searchParams.set('translate_mode', mode);
				window.location.href = url.toString();
			}

			// Update translate-language before form submission
			$ZMI.registerReady(function() {
				// Initialize Bootstrap tooltips
				$('[data-toggle="tooltip"]').tooltip();
				
				$('form.translate-forms').on('submit', function(e) {
					// Get the selected translation language (lang2)
					var lang2 = $('select[name="lang2"]').val();
					$('#translate_lang').val(lang2);
				});
				
				// Disable fields in the left column (read-only reference)
				$('.zmi-translate-left input, .zmi-translate-left textarea, .zmi-translate-left select').prop('disabled', true);
				$('.zmi-translate-left input, .zmi-translate-left textarea, .zmi-translate-left select').css('background-color', '#f8f9fa');
				
				// Remove div.contentEditable container-elements to avoid linking into normal ZMI
				$('div.contentEditable').each(function() {
					$(this).replaceWith($(this).html());
				});
				
				// Modify breadcrumb links to stay in translate tab
				var urlParams = new URLSearchParams(window.location.search);
				var lang1 = urlParams.get('lang1') || $('select[name="lang1"]').val();
				var lang2 = urlParams.get('lang2') || $('select[name="lang2"]').val();
				var viewMode = urlParams.get('translate_mode') || 'edit';
				
				$('ol.breadcrumb li a').each(function() {
					var $link = $(this);
					var href = $link.attr('href');
					
					// Remove all htmx attributes to prevent htmx interception
					$link.removeAttr('hx-get')
						.removeAttr('hx-target')
						.removeAttr('hx-swap')
						.removeAttr('hx-push-url')
						.removeAttr('hx-indicator')
						.removeAttr('hx-boost');
					
					if (href && !href.includes('manage_tab_translate')) {
						// Replace manage_main or any other action with manage_tab_translate
						var newHref = href.replace(/\/manage(_main)?(\?.*)?$/, '/manage_tab_translate');
						newHref += '?lang1=' + lang1 + '&lang2=' + lang2 + '&translate_mode=' + viewMode;
						$link.attr('href', newHref);
					}
					
					// Add click handler to ensure standard navigation
					$link.off('click').on('click', function(e) {
						e.stopPropagation();
						window.location.href = $(this).attr('href');
						return false;
					});
				});

				// Remove htmx-reactions from all tabs and force them to do page reloads
				$('nav#tabs ul.nav-tabs > li.nav-item > a').each(function() {
					var $tabLink = $(this);
					$tabLink.removeAttr('hx-get')
						.removeAttr('hx-target')
						.removeAttr('hx-trigger')
						.removeAttr('hx-swap')
						.removeAttr('hx-push-url')
						.removeAttr('hx-indicator')
						.removeAttr('hx-boost');
					$tabLink.off('click').on('click', function(e) {
						e.stopPropagation();
						window.location.href = $(this).attr('href');
						return false;
					});
				});

				// Add translate_mode parameter to icon#navbar-sitemap url
				var $sitemapIcon = $('#navbar-sitemap');
				var sitemapHref = $sitemapIcon.attr('href');
				if (sitemapHref && !sitemapHref.includes('translate_mode')) {
					sitemapHref += (sitemapHref.includes('?') ? '&' : '?') + 'lang1=' + lang1 + '&lang2=' + lang2 + '&translate_mode=' + viewMode;
					$sitemapIcon.attr('href', sitemapHref);
				}

				// Handle clickable row to switch to edit mode or navigate to child node
				$('.clickable-row').on('click', function(e) {
					var url = $(this).data('url');
					if (url) {
						// Navigate to child node's translate tab in edit mode
						window.location.href = url + (url.includes('?') ? '&' : '?') + 'lang1=' + lang1 + '&lang2=' + lang2 + '&translate_mode=' + viewMode;
					} else {
						// Switch current node to edit mode
						switch_translate_mode('edit');
					}
				});
			});
		</script>
	'''

# ----------------------------------------
# Set language options in session and request
# ----------------------------------------
def set_language_options(zmscontext, request, SESSION):
	"""Set language options in session and request"""
	
	# Set request defaults
	request.set('lang', 'ger')
	request.set('preview', 'preview')
	
	# PARAMETERS LANG-1
	coverage_delimiter = zmscontext.getDCCoverage(request).split('.')[0]
	lang1_options = zmscontext.getLangTree(zmscontext.getDCCoverage(request)[len(coverage_delimiter)+1:])
	
	if SESSION.get('lang1', '') == '':
		SESSION.set('lang1', request.get('lang1', lang1_options[0][0]))
		request.set('lang1', SESSION.get('lang1'))
	elif request.get('lang1', '') == '':
		request.set('lang1', SESSION.get('lang1'))
	else:
		SESSION.set('lang1', request.get('lang1'))
	
	request.set('lang1_options', lang1_options)
	request.set('lang1_bk', request.get('lang1'))
	
	# PARAMETERS LANG-2
	lang2_options = zmscontext.getLangTree(zmscontext.getDCCoverage(request)[len(coverage_delimiter)+1:])[1:]
	
	if SESSION.get('lang2', '') == '':
		SESSION.set('lang2', request.get('lang2', lang2_options[0][0]))
		request.set('lang2', SESSION.get('lang2'))
	elif request.get('lang2', '') == '':
		request.set('lang2', SESSION.get('lang2'))
	else:
		SESSION.set('lang2', request.get('lang2'))
	
	request.set('lang2_options', lang2_options)
	request.set('lang2_bk', request.get('lang2'))



#################################################
# MAIN
#################################################
def manage_tab_translate(self):
	"""Main entry point for the translation interface"""
	request = self.REQUEST
	response = request.RESPONSE
	SESSION = request.SESSION
	zmscontext = self
	
	# Get parameters
	lang1 = request.get('lang1', None)
	lang2 = request.get('lang2', None)
	fmName = request.get('fmName', 'form0')
	
	# Generate and return HTML
	html = renderHtml(zmscontext, request, SESSION, fmName)
	
	response.setHeader('Content-Type', 'text/html;charset=utf-8')
	return html