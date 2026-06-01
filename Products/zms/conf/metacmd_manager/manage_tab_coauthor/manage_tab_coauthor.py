from Products.zms import standard

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

def getAIHelperSettings(zmscontext):
	"""Return availability flags for AI-assisted translation helpers."""
	settings = {
		'ai_enabled': False,
		'metadata_enabled': False,
	}
	try:
		connector = zmscontext.getLLMConnector()
		if connector is not None:
			settings['ai_enabled'] = True
			settings['metadata_enabled'] = bool(connector.isFeatureEnabled('metadata_gen'))
	except Exception:
		pass
	return settings


class _FieldRequestProxy(dict):
	"""Plain request mapping used when rendering isolated field widgets."""

	def __init__(self, request, **overrides):
		dict.__init__(self)
		try:
			self.update(dict(request))
		except Exception:
			for key in request.keys():
				self[key] = request[key]
		self.update(overrides)

	def set(self, key, value):
		self[key] = value


def _make_field_request(request, same_language=False, side='right'):
	"""Create a per-field request snapshot with optional unique widget suffixes."""
	field_request = _FieldRequestProxy(request)
	if same_language and side == 'left':
		fm_name = field_request.get('fmName', 'form0')
		el_name = field_request.get('elName', '')
		field_request['fmName'] = '%s_src' % fm_name
		if el_name:
			field_request['elName'] = '%s_src' % el_name
	return field_request

# ----------------------------------------
# Basic HTML rendering function
# ----------------------------------------
def renderHtml(zmscontext, request, SESSION, fmName='form0'):
	"""Basic HTML rendering function for the translation interface"""
	ai_settings = getAIHelperSettings(zmscontext)
	
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
	html.append('<body id="manage_tab_coauthor" class="%s">'%(' '.join(['zmi',request['lang'],'manage_tab_coauthor', zmscontext.meta_id])))
	html.append(zmscontext.zmi_body_header(zmscontext,request))
	html.append('<div id="zmi-tab">')
	html.append(zmscontext.zmi_breadcrumbs(zmscontext,request))
	html.append('<div id="translate-ai-config" data-context-url="%s" data-ai-enabled="%s" data-metadata-enabled="%s"></div>' % (
		standard.html_quote(zmscontext.absolute_url()),
		str(bool(ai_settings['ai_enabled'])).lower(),
		str(bool(ai_settings['metadata_enabled'])).lower(),
	))
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
	view_active = ' active' if translate_mode == 'view' else ''
	edit_active = ' active' if translate_mode == 'edit' else ''
	html.append('<button id="switch_view" type="button" title="View Mode: Rendered HTML in two languages side-by-side" class="btn py-0 px-3%s" onclick="switch_translate_mode(\'view\')">VIEW</button>' % view_active)
	html.append('<button id="switch_edit" type="button" title="Edit Mode: Edit HTML-form of two languages side-by-side" class="btn py-0 px-3%s" onclick="switch_translate_mode(\'edit\')">EDIT</button>' % edit_active)
	html.append('</div>')

	html.append('</legend>')

	html.append('<div id="manage_tab_coauthor_body" class="card-body p-0 m-0">')

	# Render based on view mode
	if translate_mode == 'view':
		html.append(renderViewMode(zmscontext, request))
	else:
		html.append(renderEditMode(zmscontext, request, ai_settings))
	
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
	html.append(renderGoogleTranslate(request))
	
	# Add styles and scripts
	html.append(renderStyles())
	html.append(renderScripts())
	
	html.append('</body>')
	html.append('</html>')
	
	return '\n'.join(html)


# ----------------------------------------
# Render edit mode with form fields
# ----------------------------------------
def renderEditMode(zmscontext, request, ai_settings=None):
	"""Render edit mode with form fields"""
	ai_settings = ai_settings or {}
	same_language = request.get('lang1') == request.get('lang2')
	auto_button_label = same_language and 'Auto-Editing' or 'Auto-Translate'
	auto_button_title = same_language and 'Improve text quality and complete missing metadata using the configured LLM service.' or 'Auto-translate from %s to %s' % (
		request.get('lang1'),
		request.get('lang2'),
	)
	button_disabled = same_language and not ai_settings.get('ai_enabled', False)
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
			btn_disabled_attr = button_disabled and ' disabled="disabled"' or ''
			html.append('''<button type="button"
				id="translate-auto-action"
				class="btn btn-sm btn-success form-control-sm w-auto m-1"
				onclick="triggerAutoTranslate()"
				title="%s"%s>%s</button>''' % (
					standard.html_quote(auto_button_title),
					btn_disabled_attr,
					auto_button_label,
				))

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
			html.append('<tr class="form-group-row" data-objattr-id="%s" data-objattr-label="%s">' % (
				standard.html_quote(metaObjAttr['id']),
				standard.html_quote(zmscontext.getObjAttrLabel(metaObjAttr)),
			))
			
			# Render for both languages
			for si in ['left', 'right']:
				old_obj_attr_name_prefix = request.get('objAttrNamePrefix', '')
				old_obj_attr_name_suffix = request.get('objAttrNameSuffix', '')
				if same_language and si == 'left':
					request.set('objAttrNameSuffix', '_src')
				else:
					request.set('objAttrNamePrefix', '')
					request.set('objAttrNameSuffix', '')
				try:
					lang = request.get('lang1' if si == 'left' else 'lang2')
					request.set('lang', lang)
					elName = zmscontext.getObjAttrName(metaObjAttr, lang)
					elLabel = '%s [%s_%s]' % (zmscontext.getObjAttrLabel(metaObjAttr), metaObjAttr['id'], lang)
					is_mandatory = metaObjAttr.get('mandatory')
					
					html.append('<td class="form-group-cell zmi-translate-block zmi-translate-%s" width="50%%" valign="top" data-objattr-id="%s" data-objattr-label="%s" data-lang="%s">' % (
						si,
						standard.html_quote(metaObjAttr['id']),
						standard.html_quote(zmscontext.getObjAttrLabel(metaObjAttr)),
						standard.html_quote(lang),
					))
					html.append('<div class="form-group row" id="tr_%s">' % elName)
					html.append('<label for="%s" class="col-sm-3 control-label%s">' % (elName, ' mandatory' if is_mandatory else ''))
					html.append('<span>%s</span>' % elLabel)
					html.append('</label>')
					html.append('<div class="col-sm-9">')
					
					# Render the input field
					try:
						field_request = _make_field_request(request, same_language=same_language, side=si)
						input_html = zmscontext.getObjInput(metaObjAttr['id'], field_request)
						html.append(input_html)
					except Exception as e:
						html.append('<span class="text-danger">Error rendering field: %s</span>' % str(e))
					
					html.append('</div>')
					html.append('</div>')
					html.append('</td>')
				finally:
					request.set('objAttrNamePrefix', old_obj_attr_name_prefix)
					request.set('objAttrNameSuffix', old_obj_attr_name_suffix)
			
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
		
		html.append('<td class="form-group-cell zmi-translate-%s %s translate_mode-cell" width="50%%">' % (si, notranslate_class))
		
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
		translate_url = '%s/manage_tab_coauthor' % (childNode.absolute_url())
		
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
			
			html.append('<td class="form-group-cell zmi-translate-%s %s translate_mode-cell">' % (si, notranslate_class))
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
def renderGoogleTranslate(request):
	"""Render Google Translate widget HTML and JavaScript"""
	if request.get('lang1') == request.get('lang2'):
		return '''
			<script>
				//<!--  Editing-Mode: Source and target languages are the same.
				setTimeout(function() {
				// Reset RTE fields to apply translation
				if ($('div[id*="zmiRichtextEditor"]:visible').length > 0) {
						$('.form-richtext-wysiwyg > .col-sm-12 > .btn-group > span.btn').click()
					}
				}, 1000);
			//-->
			</script>
		'''
	return '''
		<!-- Translation Mode: Google Translate Element -->
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
					var $leftInput = $leftCell.find('input.form-control.datatype-11, textarea');
					var $rightInput = $rightCell.find('input.form-control.datatype-11, textarea');
					
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
			$('body').append('<div id="translate-progress" style="position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);background:white;padding:20px;border:2px solid #007bff;border-radius:5px;z-index:10000;"><i class="fas fa-spinner fa-spin mr-1"></i> Translating... <span id="progress-counter">0/' + totalFields + '</span></div>');
			
			// Process each row
			$('.form-group-row').each(function() {
				var $row = $(this);
				var $leftCell = $row.find('.zmi-translate-block.zmi-translate-left');
				var $rightCell = $row.find('.zmi-translate-block.zmi-translate-right');
				
				if ($leftCell.length && $rightCell.length) {
					// Find input fields
					var $leftInput = $leftCell.find('input.form-control.datatype-11, textarea');
					var $rightInput = $rightCell.find('input.form-control.datatype-11, textarea');
					
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
				if ($('div[id*="zmiRichtextEditor"]:visible').length > 0) {
					$('.form-richtext-wysiwyg > .col-sm-12 > .btn-group > span.btn').click()
				}
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


			/* ################################################### */
			/* Styles for the translate mode toggle buttons */
			/* ################################################### */

			.translate_mode-toggle {
				--anim_duration: .35s;
				--toggle_color: #354f67;
				--btn_width: 5rem;
				margin: -.1rem -.85rem 0 0;
				background-color: white;
			}
			.translate_mode-toggle .btn {
				width:var(--btn_width);
				border:1px solid var(--toggle_color);
			}
			.translate_mode-toggle .btn.active {
				color:white;
				background-color:var(--toggle_color);
			}
			.translate_mode-toggle:hover .btn.active {
				color:unset;
				background-color:unset;
				transition: var(--anim_duration);
			}
			.translate_mode-toggle .btn:before {
				content:"\\00A0";
				display:block;
				background-color:var(--toggle_color);
				z-index:-1;
				border-radius:.2rem;
				width:calc(var(--btn_width) - 1px);
				position:absolute;
				left:0;
				top:-1px;
				border:1px solid transparent;
				padding:0;
			}
			.translate_mode-toggle:hover .btn:before {
				display:none;
			}
			.translate_mode-toggle .btn:not(.active):hover {
				color:white;
				transition: var(--anim_duration);
			}
			.translate_mode-toggle #switch_view.btn:hover:before {
				display:block;
				animation:slide_view var(--anim_duration) ease-in-out 0s 1 forwards;
			}
			.translate_mode-toggle #switch_edit.btn:hover:before {
				display:block;
				animation:slide_edit var(--anim_duration) ease-in-out 0s 1 forwards;
			}
			@keyframes slide_edit {
				0% {
					transform:translateX(-100%);
				}
				100% {
					transform:translateX(0%);
					border-top-left-radius:0;
					border-bottom-left-radius:0;
				}
			}
			@keyframes slide_view {
				0% {
					transform:translateX(100%);
				}
				100% {
					transform:translateX(0%);
					border-top-right-radius:0;
					border-bottom-right-radius:0;
				}
			}
			.translate_mode-toggle .btn.active {
				cursor: default;
				opacity: 1;
			}
			.translate_mode-toggle:hover:has(.btn:not(.active):hover) .btn.active {
				color:#545b62;
				transition: var(--anim_duration);
			}
			.translate_mode-toggle:hover .btn:hover {
				color:white;
				transition: var(--anim_duration);
			}
			/* ################################################### */

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
				background-color: #d1e5f688;
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
			.zmi .content-view-table .contentEditable > div[class*="col-"] {
				max-width:100% !important;
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
			.properties-table .zmi-translate-block > .form-group.row > div.col-sm-5.col-md-4.col-lg-3 {
				/* input-type: date */
				width:unset !important;
				max-width:unset !important;
			}

			/* Form Groups */
			.form-group-cell {
				font-size: 0.9rem;
			}
			.form-group-cell .form-group {
				margin-bottom: 0;
			}
			.form-group-cell .description,
			.form-group-cell .control-label {
				font-weight: 600;
			}
			.zmi-translate-right {
				background-color: aliceblue;
			}
			.form-group-cell .control-label.mandatory::after {
				content: " *";
				color: red;
			}
			
			/* Input Fields */
			.form-group-cell .input-group {
				flex-wrap: nowrap !important;
			}
			.form-group-cell >.input-group {
				display:block;
			}
			.form-group-cell input[type="text"],
			.form-group-cell textarea,
			.form-group-cell select {
				width: 100%;
			}
			.form-group-cell textarea {
				min-height: 100px;
			}
			.form-group-cell a.ZMSGraphic_extEdit_action {
				pointer-events: none !important;
				cursor: not-allowed !important;
			}
			.form-group-cell a.ZMSGraphic_extEdit_action .zmi-zoom-in {
				opacity: 0;
			}
			.form-group-cell a.ZMSGraphic_extEdit_action img {
				object-fit: contain;
			}
			.ai-diff-wrapper {
				margin-top: 0.35rem;
			}
			.ai-source-wrapper {
				margin-top: 0.35rem;
			}
			.ai-diff-hint {
				font-size: 0.78rem;
				margin-top: 0.25rem;
				color: #607080;
			}
			.ai-diff-editor {
				background: #ffffff;
				border: 1px solid #ced4da;
				border-radius: 0.25rem;
				padding: 0.55rem 0.75rem;
				min-height: 10rem;
				max-height: 20rem;
				overflow: auto;
				white-space: pre-wrap;
				word-break: break-word;
				font-family: SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
				font-size: 0.88rem;
				line-height: 1.45;
			}
			.ai-source-editor {
				color: #2f3f50;
			}
			.ai-diff-editor.ai-diff-editor-inline {
				min-height: 2.35rem;
			}
			.ai-source-editor.ai-source-editor-inline {
				min-height: 2.35rem;
			}
			.ai-diff-editor ins,
			.ai-diff-editor del {
				cursor: pointer;
				padding: 0 0.1rem;
				border-radius: 0.12rem;
				text-decoration-thickness: 0.08rem;
			}
			.ai-diff-editor ins {
				background-color: #d4edda;
				color: #155724;
				text-decoration: none;
			}
			.ai-diff-editor del {
				background-color: #f8d7da;
				color: #7f1d1d;
				text-decoration: line-through;
			}
			.ai-diff-editor ins.ai-change-rejected {
				opacity: 0.35;
				background-color: #e2e3e5;
				color: #495057;
				text-decoration: line-through;
			}
			.ai-diff-editor del.ai-change-restored {
				opacity: 1;
				background-color: #fff3cd;
				color: #7a5200;
				text-decoration: none;
			}
			.ai-diff-editor ins:hover,
			.ai-diff-editor del:hover {
				box-shadow: inset 0 0 0 1px rgba(0, 0, 0, 0.25);
			}
			.form-group-cell.zmi-translate-right.warning-maxlength .col-sm-9:has(>textarea.form-control):before,
			.form-group-cell.zmi-translate-right.warning-maxlength .col-sm-9 div.form-group:has(textarea,input):before {
				content:"Maximum Characters 5000 exeeded: Auto-Translation will be rejected.";
				display:block;
				position:absolute;
				z-index:1;
				margin:3rem;
				text-align:center;
				width:calc(100% - 6rem);
				padding: 1rem;
				background-color:#f8d7da;
				border-radius:.25rem;
				border:1px solid #f5c6cb;
				color:#721c24
			}
			.form-group-cell.zmi-translate-right.warning-maxlength .col-sm-9:has(>textarea.form-control):before {
				margin:2rem;
			}

			/* Rich Text Editors */
			.form-group-cell .zmi-richtext {
				min-height: 200px;
			}
			.form-group-cell .form-richtext-wysiwyg .col-sm-12 .btn-group.pull-right .btn {
				display: block !important;
			}
			.form-group-cell .form-richtext-standard > div.col-sm-12:has(.float-left) {
				white-space:nowrap;
				max-height:2rem
			}
			.form-group-cell .form-richtext-standard > div.col-sm-12 > .float-right {
				position:absolute;
				right:1rem
			}
			.form-group-cell .form-richtext-standard > div.col-sm-12 .btn-secondary:has(.fa-eye-slash) {
				background-color: transparent;
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
					display:none;
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
# ----------------------------------------
def renderScripts():
	"""Render JavaScript code"""
	return r'''
		<script>
			function getTranslateLanguages() {
				return {
					lang1: $('select[name="lang1"]').val(),
					lang2: $('select[name="lang2"]').val()
				};
			}

			function getTranslateAIConfig() {
				var node = document.getElementById('translate-ai-config');
				var dataset = node ? node.dataset : {};
				return {
					contextUrl: dataset.contextUrl || '',
					aiEnabled: dataset.aiEnabled === 'true',
					metadataEnabled: dataset.metadataEnabled === 'true'
				};
			}

			function getAutoActionButton() {
				return $('#translate-auto-action');
			}

			function updateAutoActionButton() {
				var langs = getTranslateLanguages();
				var config = getTranslateAIConfig();
				var sameLanguage = langs.lang1 === langs.lang2;
				var $button = getAutoActionButton();
				if (!$button.length) {
					return;
				}
				if (sameLanguage) {
					$button.text('Auto-Editing');
					$button.attr('title', config.aiEnabled
						? 'Improve text quality and complete missing metadata using the configured LLM service.'
						: 'Auto-Editing requires a configured ZMSLLMConnector.');
					$button.prop('disabled', !config.aiEnabled);
				}
				else {
					$button.text('Auto-Translate');
					$button.attr('title', 'Auto-translate from ' + langs.lang1 + ' to ' + langs.lang2);
					$button.prop('disabled', false);
				}
			}

			function extractJsonObject(text) {
				if (!text) {
					return null;
				}
				var fenced = text.match(/```(?:json)?\s*([\s\S]*?)```/i);
				if (fenced && fenced[1]) {
					text = fenced[1];
				}
				text = $.trim(text);
				var start = text.indexOf('{');
				if (start < 0) {
					return null;
				}
				var depth = 0;
				var inString = false;
				var escaped = false;
				for (var i = start; i < text.length; i++) {
					var ch = text.charAt(i);
					if (escaped) {
						escaped = false;
						continue;
					}
					if (ch === '\\') {
						escaped = true;
						continue;
					}
					if (ch === '"') {
						inString = !inString;
						continue;
					}
					if (inString) {
						continue;
					}
					if (ch === '{') {
						depth++;
					}
					else if (ch === '}') {
						depth--;
						if (depth === 0) {
							try {
								return JSON.parse(text.substring(start, i + 1));
							}
							catch (error) {
								return null;
							}
						}
					}
				}
				return null;
			}

			function getEditableField($cell) {
				return $cell.find('textarea, input.form-control.datatype-11').filter(function() {
					return $(this).closest('.input-group-append, .input-group-prepend').length === 0;
				}).first();
			}

			function collectAutoEditRows() {
				var rows = [];
				$('.form-group-row').each(function() {
					var $row = $(this);
					var $leftCell = $row.find('.zmi-translate-block.zmi-translate-left');
					var $rightCell = $row.find('.zmi-translate-block.zmi-translate-right');
					var $leftInput = getEditableField($leftCell);
					var $rightInput = getEditableField($rightCell);
					if (!$leftInput.length || !$rightInput.length) {
						return;
					}
					rows.push({
						attrId: $row.data('objattr-id') || $leftCell.data('objattr-id') || '',
						label: $row.data('objattr-label') || $leftCell.data('objattr-label') || '',
						sourceValue: $leftInput.val() || '',
						sourceInput: $leftInput,
						targetValue: $rightInput.val() || '',
						targetInput: $rightInput,
						isRichtext: $leftCell.find('.form-richtext-standard, .form-richtext-wysiwyg').length > 0,
						isMetadata: /titlealt|dc_description|dc_subject|keywords|subject|summary/i.test(String($row.data('objattr-id') || ''))
					});
				});
				return rows;
			}

			function showTranslateProgress(text) {
				$('#translate-progress').remove();
				$('body').append('<div id="translate-progress" style="position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);background:white;padding:20px;border:2px solid #007bff;border-radius:5px;z-index:10000;"><i class="fas fa-spinner fa-spin mr-1"></i> ' + text + '</div>');
			}

			function hideTranslateProgress() {
				$('#translate-progress').remove();
			}

			function buildAutoEditPrompt(rows, sourceLang, targetLang, metadataEnabled) {
				var payload = {
					source_language: sourceLang,
					target_language: targetLang,
					same_language_mode: true,
					metadata_generation_enabled: metadataEnabled,
					fields: rows.map(function(row) {
						return {
							id: row.attrId,
							label: row.label,
							source_value: row.sourceValue,
							current_target_value: row.targetValue,
							metadata_field: row.isMetadata
						};
					})
				};

				return [
					'You are a CMS editorial assistant working in same-language editing mode.',
					'Return only valid JSON and no markdown.',
					'JSON schema: {"fields": {"<field_id>": "<suggested text>"}}',
					'Keep the language exactly as ' + targetLang + '.',
					'Improve clarity, grammar, style, and consistency without changing the factual meaning.',
					'Do not invent facts, numbers, names, or claims that are not supported by the input.',
					(metadataEnabled
						? 'Fill missing or weak metadata fields when they can be derived from the existing content.'
						: 'Do not generate extra metadata beyond clear text improvements.'),
					'Omit any field that should stay unchanged.',
					'Ignore file names, media references, and technical values.',
					'Input JSON:',
					JSON.stringify(payload, null, 2)
				].join('\n');
			}

			function requestHtmlDiff(originalText, changedText) {
				var config = getTranslateAIConfig();
				return $.ajax({
					type: 'POST',
					url: $ZMI.get_rest_api_url(config.contextUrl) + '/get_htmldiff',
					dataType: 'html',
					data: {
						lang: getZMILang(),
						original: originalText || '',
						changed: changedText || ''
					}
				});
			}

			function cleanupDiffEditors(rows) {
				rows.forEach(function(row) {
					var $target = row.targetInput;
					var $existingEditor = $target.data('aiDiffEditor');
					if ($existingEditor && $existingEditor.length) {
						$existingEditor.closest('.ai-diff-wrapper').remove();
					}
					$target.removeData('aiDiffEditor');
					$target.removeClass('d-none ai-diff-source');
				});
			}

			function renderLeftSourceView(row) {
				var $source = row.sourceInput;
				if (!$source || !$source.length) {
					return;
				}
				var isInline = $source.is('input.form-control.datatype-11');
				var $editor = $source.data('aiSourceEditor');
				if (!$editor || !$editor.length) {
					var $wrapper = $('<div class="ai-diff-wrapper ai-source-wrapper"></div>');
					var editorClass = isInline ? 'ai-diff-editor ai-diff-editor-inline ai-source-editor' : 'ai-diff-editor ai-source-editor';
					$editor = $('<div></div>').addClass(editorClass);
					$wrapper.append($editor);
					$source.after($wrapper);
					$source.data('aiSourceEditor', $editor);
				}
				if (row.isRichtext) {
					$editor.html(row.sourceValue || '');
				}
				else {
					$editor.text(row.sourceValue || '');
				}
				$source.addClass('d-none ai-source-hidden');
			}

			function syncLeftSourceViews(rows) {
				rows.forEach(function(row) {
					renderLeftSourceView(row);
				});
			}

			function renderAutoEditDiff(row, diffHtml) {
				var $target = row.targetInput;
				var isInline = $target.is('input.form-control.datatype-11');
				var $wrapper = $('<div class="ai-diff-wrapper"></div>');
				var editorClass = isInline ? 'ai-diff-editor ai-diff-editor-inline' : 'ai-diff-editor';
				var $editor = $('<div></div>').addClass(editorClass).html(diffHtml || '');
				var hintText = 'Click green additions to reject them. Click red deletions to restore them.';
				$wrapper.append($editor);
				$wrapper.append($('<div class="ai-diff-hint"></div>').text(hintText));
				$target.addClass('d-none ai-diff-source');
				$target.after($wrapper);
				$target.data('aiDiffEditor', $editor);
			}

			function finalizeDiffEditorText($editor, plainTextMode) {
				if (!$editor || !$editor.length) {
					return '';
				}
				var $clone = $('<div></div>').html($editor.html());
				$clone.find('ins').each(function() {
					var $ins = $(this);
					if ($ins.hasClass('ai-change-rejected')) {
						$ins.remove();
					}
					else {
						$ins.replaceWith($ins.html());
					}
				});
				$clone.find('del').each(function() {
					var $del = $(this);
					if ($del.hasClass('ai-change-restored')) {
						$del.replaceWith($del.html());
					}
					else {
						$del.remove();
					}
				});
				$clone.find('div.diff').each(function() {
					$(this).replaceWith($(this).html());
				});
				if (!plainTextMode) {
					return $clone.html();
				}
				$clone.find('br').replaceWith('\n');
				$clone.find('p,div,li,tr,h1,h2,h3,h4,h5,h6').each(function() {
					$(this).append('\n');
				});
				var text = $clone.text().replace(/\u00a0/g, ' ');
				text = text.replace(/\n{3,}/g, '\n\n');
				return text;
			}

			function commitAutoEditDiffEditors() {
				$('.zmi-translate-right textarea, .zmi-translate-right input.form-control.datatype-11').each(function() {
					var $target = $(this);
					var $editor = $target.data('aiDiffEditor');
					if ($editor && $editor.length) {
						var plainTextMode = $target.is('input.form-control.datatype-11');
						$target.val(finalizeDiffEditorText($editor, plainTextMode));
					}
				});
			}

			function toggleDiffToken($token) {
				if ($token.is('ins')) {
					$token.toggleClass('ai-change-rejected');
				}
				else if ($token.is('del')) {
					$token.toggleClass('ai-change-restored');
				}
				var $cell = $token.closest('td.form-group-cell.zmi-translate-right');
				if ($cell.length) {
					updateMaxLengthWarningForCell($cell);
				}
			}

			function getTextLengthWithoutHtml(rawValue) {
				var text = $('<div></div>').html(rawValue || '').text();
				return text.length;
			}

			function getCurrentRightCellValue($cell) {
				var $input = $cell.find('textarea, input.form-control.datatype-11').filter(function() {
					return $(this).closest('.input-group-append, .input-group-prepend').length === 0;
				}).first();
				if (!$input.length) {
					return '';
				}
				var $editor = $input.data('aiDiffEditor');
				if ($editor && $editor.length) {
					var plainTextMode = $input.is('input.form-control.datatype-11');
					return finalizeDiffEditorText($editor, plainTextMode);
				}
				return $input.val() || '';
			}

			function updateMaxLengthWarningForCell($cell) {
				var rawValue = getCurrentRightCellValue($cell);
				var textLength = getTextLengthWithoutHtml(rawValue);
				$cell.toggleClass('warning-maxlength', textLength > 5000);
			}

			function updateAllMaxLengthWarnings() {
				$('td.form-group-cell.zmi-translate-right').each(function() {
					updateMaxLengthWarningForCell($(this));
				});
			}

			function applyAutoEditResult(rows, result) {
				var fields = {};
				if (result && typeof result === 'object') {
					fields = result.fields && typeof result.fields === 'object' ? result.fields : result;
				}
				cleanupDiffEditors(rows);
				var updated = 0;
				var jobs = [];
				rows.forEach(function(row) {
					var suggestion = fields[row.attrId];
					if (typeof suggestion === 'string' && $.trim(suggestion) !== '') {
						var job = $.Deferred();
						requestHtmlDiff(row.targetValue || '', suggestion).done(function(diffHtml) {
							renderAutoEditDiff(row, diffHtml);
							row.targetInput.css('background-color', '#ffffcc');
						}).fail(function() {
							row.targetInput.removeClass('d-none ai-diff-source');
							row.targetInput.val(suggestion);
							row.targetInput.css('background-color', '#ffffcc');
						}).always(function() {
							job.resolve();
						});
						jobs.push(job.promise());
						updated++;
					}
				});
				if (!jobs.length) {
					return $.Deferred().resolve(updated).promise();
				}
				return $.when.apply($, jobs).then(function() {
					updateAllMaxLengthWarnings();
					return updated;
				});
			}

			function runSameLanguageAutoEdit() {
				var config = getTranslateAIConfig();
				if (!config.aiEnabled) {
					alert('Auto-Editing requires a configured ZMSLLMConnector.');
					return;
				}
				var langs = getTranslateLanguages();
				var rows = collectAutoEditRows();
				if (!rows.length) {
					alert('No editable text fields found.');
					return;
				}
				syncLeftSourceViews(rows);
				var prompt = buildAutoEditPrompt(rows, langs.lang1, langs.lang2, config.metadataEnabled);
				showTranslateProgress('Auto-editing content...');
				$.ajax({
					url: $ZMI.get_rest_api_url(config.contextUrl) + '/llm_chat',
					method: 'POST',
					dataType: 'json',
					data: {
						message: prompt,
						agent_mode: '0',
						preserve_html: '1'
					}
				}).done(function(response) {
					hideTranslateProgress();
					if (response && response.error) {
						var errorMessage = typeof response.error === 'string' ? response.error : (response.error.message || 'LLM request failed.');
						alert(errorMessage);
						return;
					}
					var parsed = extractJsonObject(response && response.reply ? response.reply : '');
					if (!parsed) {
						alert('The LLM did not return valid JSON suggestions.');
						return;
					}
					applyAutoEditResult(rows, parsed).done(function(updated) {
						alert('Auto-Editing completed for ' + updated + ' field(s). Click highlighted changes to accept/reject them before saving.');
					});
				}).fail(function(xhr) {
					hideTranslateProgress();
					var message = 'Auto-Editing request failed.';
					if (xhr && xhr.responseJSON && xhr.responseJSON.error) {
						message = xhr.responseJSON.error.message || xhr.responseJSON.error;
					}
					alert(message);
				});
			}

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

			window.triggerAutoTranslate = function() {
				var langs = getTranslateLanguages();
				if (langs.lang1 === langs.lang2) {
					if (confirm('This will improve the text quality and complete missing metadata in ' + langs.lang2 + '. Continue?')) {
						runSameLanguageAutoEdit();
					}
					return;
				}
				if (typeof window.translateAndCopy === 'function') {
					if (confirm('This will copy and translate content from ' + langs.lang1 + ' to ' + langs.lang2 + '. Continue?')) {
						window.translateAndCopy();
					}
				}
			};

			// Update translate-language before form submission
			$ZMI.registerReady(function() {
				// Initialize Bootstrap tooltips
				$('[data-toggle="tooltip"]').tooltip();
				updateAutoActionButton();
				$(document).off('click.aiDiffToggle').on('click.aiDiffToggle', '.ai-diff-editor ins, .ai-diff-editor del', function(e) {
					e.preventDefault();
					e.stopPropagation();
					toggleDiffToken($(this));
				});
				
				$('form.translate-forms').on('submit', function(e) {
					commitAutoEditDiffEditors();
					updateAllMaxLengthWarnings();
					// Get the selected translation language (lang2)
					var lang2 = $('select[name="lang2"]').val();
					$('#translate_lang').val(lang2);
				});
				$(document).off('input.aiMaxLength keyup.aiMaxLength paste.aiMaxLength change.aiMaxLength', '.zmi-translate-right textarea, .zmi-translate-right input.form-control.datatype-11').on('input.aiMaxLength keyup.aiMaxLength paste.aiMaxLength change.aiMaxLength', '.zmi-translate-right textarea, .zmi-translate-right input.form-control.datatype-11', function() {
					var $cell = $(this).closest('td.form-group-cell.zmi-translate-right');
					if ($cell.length) {
						updateMaxLengthWarningForCell($cell);
					}
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
					
					if (href && !href.includes('manage_tab_coauthor')) {
						// Replace manage_main or any other action with manage_tab_coauthor
						var newHref = href.replace(/\/manage(_main)?(\?.*)?$/, '/manage_tab_coauthor');
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
				updateAllMaxLengthWarnings();
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
	lang2_options = zmscontext.getLangTree(zmscontext.getDCCoverage(request)[len(coverage_delimiter)+1:])
	default_lang2 = request.get('lang1')
	for opt in lang2_options:
		if opt[0] != request.get('lang1'):
			default_lang2 = opt[0]
			break
	
	if SESSION.get('lang2', '') == '':
		SESSION.set('lang2', request.get('lang2', default_lang2))
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
def manage_tab_coauthor(self):
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