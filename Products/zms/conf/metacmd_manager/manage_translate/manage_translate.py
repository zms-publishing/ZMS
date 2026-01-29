## Script (Python) "manage_translate"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=*** DO NOT DELETE OR MODIFY ***
##

#################################################
# Version 6.0.0, Refactored from DTML to Python
# Original DTML version converted to External Python Method
# Date: 2026-01-29
#################################################


def renderHtml(zmscontext, request, SESSION, fmName='form0'):
	"""Main HTML rendering function for the translation interface"""
	
	# Set request defaults
	request.set('lang', 'ger')
	request.set('preview', 'preview')
	request.set('fmName', fmName)
	
	html = []
	
	try:
		# PARAMETERS LANG-1
		lang1_options = zmscontext.getLangTree(zmscontext.getDCCoverage(request)[len('global.'):])
		
		if SESSION.get('lang1', '') == '':
			SESSION.set('lang1', request.get('lang1', lang1_options[0][0]))
			request.set('lang1', SESSION.get('lang1'))
		elif request.get('lang1', '') == '':
			request.set('lang1', SESSION.get('lang1', lang1_options[0][0]))
		else:
			SESSION.set('lang1', request.get('lang1'))
		
		request.set('lang1_options', lang1_options)
		request.set('lang1_bk', request.get('lang1'))
		
		# PARAMETERS LANG-2
		lang2_options = zmscontext.getLangTree(zmscontext.getDCCoverage(request)[len('global.'):])[1:]
		
		if SESSION.get('lang2', '') == '':
			SESSION.set('lang2', request.get('lang2', lang2_options[0][0]))
			request.set('lang2', SESSION.get('lang2'))
		elif request.get('lang2', '') == '':
			request.set('lang2', SESSION.get('lang2', lang2_options[0][0]))
		else:
			SESSION.set('lang2', request.get('lang2'))
		
		request.set('lang2_options', lang2_options)
		request.set('lang2_bk', request.get('lang2'))
		
		# Start HTML output
		html.append('<!DOCTYPE html>')
		html.append('<html lang="en">')
		html.append(zmscontext.zmi_html_head(zmscontext, request))
		html.append('<body class="zmi" id="manage_translate" hx-disable="hx-disable">')
		html.append('<header class="navbar navbar-nav navbar-expand navbar-dark notranslate">')
		html.append(zmscontext.zmi_breadcrumbs_obj_path(zmscontext, request))
		html.append('</header>')
		
		# Debug info
		html.append('''
			<div class="debug_info" title="DEBUG INFO">
				<i class="fas fa-flag"></i>
				<div class="code">
					REQUEST lang1: %s<br />
					REQUEST lang2: %s<br />
					SESSION lang1: %s<br />
					SESSION lang2: %s<br />
				</div>
			</div>''' % (
				request.get('lang1', ''),
				request.get('lang2', ''),
				SESSION.get('lang1', ''),
				SESSION.get('lang2', '')
		))
		
		# Form
		html.append('<form id="%s" method="get">' % fmName)
		html.append('<table cellspacing="0" cellpadding="0" border="0" width="100%">')
		html.append('<tr valign="top">')
		
		# Get child nodes
		childNodes = [x for x in zmscontext.getObjChildren('e', request) if x.isPageElement()]
		exclude_langs = []
		
		# Render left and right columns (header row)
		for si in ['left', 'right']:
			lang_req_key = 'lang1' if si == 'left' else 'lang2'
			notranslate_class = 'notranslate' if si == 'left' else 'translate'
			
			html.append('<td class="zmi-translate-%s %s" width="50%%">' % (si, notranslate_class))
			html.append('<span class="zmi-translate-element-id notranslate">')
			html.append('<a title="Open this Content Node in a New Browser Window ..." href="%s/manage_properties?lang=%s" target="_blank">%s</a>&nbsp;&nbsp;' % (
				zmscontext.absolute_url(),
				request.get(lang_req_key),
				zmscontext.id
			))
			html.append('</span>')
			
			# Language selector
			lang_options_html = []
			for opt in request.get(lang_req_key + '_options'):
				selected = ' selected="selected"' if opt[0] == request.get(lang_req_key) else ''
				lang_options_html.append('<option value="%s"%s>%s</option>' % (opt[0], selected, opt[1]['label']))
			
			html.append('<select class="form-control form-control-sm d-inline w-auto lang notranslate" name="%s" onchange="document.getElementById(\'%s\').submit();">' % (lang_req_key, fmName))
			html.extend(lang_options_html)
			html.append('</select>')
			
			# Set language for content rendering
			request.set('lang', request.get(lang_req_key))
			
			html.append('<div id="%s" class="zmi-translate-element">' % zmscontext.id)
			html.append('<div class="zmiRenderShort" id="contentEditable_%s_%s">' % (zmscontext.id, request.get('lang')))
			
			# Render content based on meta_id
			if zmscontext.meta_id not in ['ZMSDocument', 'ZMSFolder', 'ZMS']:
				html.append(zmscontext.getBodyContent(request))
			else:
				html.append('<h1>%s</h1>' % zmscontext.getTitle(request))
				desc = zmscontext.getDCDescription(request).replace('\n', '<br />')
				html.append('<p class="description">%s</p>' % desc)
			
			html.append('</div>')
			html.append('</div>')
			html.append('</td>')
		
		html.append('</tr>')
		
		# Render child nodes
		for childNode in childNodes:
			html.append('<tr valign="top">')
			
			for si in ['left', 'right']:
				lang_req_key = 'lang1' if si == 'left' else 'lang2'
				notranslate_class = 'notranslate' if si == 'left' else 'translate'
				
				request.set('lang', request.get(lang_req_key + '_bk'))
				
				inactive_style = ''
				inactive_title = ''
				if not childNode.isActive(request):
					inactive_style = ' style="background-color:#999"'
					inactive_title = ' title="Inactive"'
				
				save_icon = ''
				if si != 'left':
					save_icon = '<i class="fas fa-arrow-down" title="%s: Save (Automatic Pre-) Translation" style="cursor:pointer;" onclick="save(this)"></i>' % request.get('lang')
				
				html.append('<td class="article zmi-translate-%s %s">' % (si, notranslate_class))
				html.append('<span class="zmi-translate-element-id notranslate"%s%s> <a title="Open this Content Node in a New Browser Window ..." href="%s/manage?lang=%s" target="_blank">%s</a> %s</span>' % (
					inactive_title,
					inactive_style,
					childNode.absolute_url(),
					request.get('lang'),
					childNode.id,
					save_icon
				))
				html.append('<div id="%s_%s" class="zmi-translate-element">' % (str(childNode), childNode.id))
				html.append('<div class="zmiRenderShort" contenteditable="true" id="contentEditable_%s_%s">%s</div>' % (childNode.id, request.get('lang'), childNode.renderShort(request)))
				html.append('</div>')
				html.append('</td>')
			
			html.append('</tr>')
		
		html.append('</table>')
		html.append('</form>')
		
		# Google Translate Element
		html.append(renderGoogleTranslate())
		
	except Exception as e:
		html.append('''
			<div class="alert alert-danger m-3">
				<p>ERROR: Translation not possible. Maybe not second language configured.</p>
				<pre>%s</pre>
			</div>''' % str(e))
	
	# Add styles and scripts
	html.append(renderStyles())
	html.append(renderScripts())
	
	html.append('</body>')
	html.append('</html>')
	
	return '\n'.join(html)


def renderGoogleTranslate():
	"""Render Google Translate widget HTML and JavaScript"""
	return '''
		<!-- Google Translate Element -->
		<div id="google_translate_element" style="display:block"></div>
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
			var lang1 = $('select[name="lang1"] option:first').val(); // text to be translated
			var lang2 = $('select[name="lang2"] option:first').val(); // translation target
			lang1 = langmap[lang1];
			lang2 = langmap[lang2]

			// Initialize Google Translate element
			function googleTranslateElementInit() {
				new google.translate.TranslateElement({
				pageLanguage: lang1,   // source language
				includedLanguages: lang2, // target language(s)
				layout: google.translate.TranslateElement.InlineLayout.SIMPLE
				}, 'google_translate_element');
			}

			// After initialization, set the dropdown value and trigger change
			function setGoogleTranslate(langCode) {
				var $combo = $('#google_translate_element select.goog-te-combo');
				if ($combo.length) {
				$combo.val(langCode);
				$combo.trigger('change');
				}
			}

			// Once the widget is ready select target-language
			$(document).ready(function() {
				// Wait a bit for the widget to load
				setTimeout(function() {
				setGoogleTranslate(lang2);
				}, 1000);
			});
		//-->
		</script>
		<script src="https://translate.google.com/translate_a/element.js?cb=googleTranslateElementInit"></script>
		<!-- /Google Translate Element -->
	'''


def renderStyles():
	"""Render CSS styles"""
	return '''
		<style>
			.zmi > form {
				margin-top:-1px;
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
			}
			.zmi .debug_info .code {
				display:none;
				background: #ffffffa8;
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
				color: white;
				right: 0;
				top: 0;
				padding: .75rem;
			}
			.zmi-translate-left {
				padding:4px;
				background-color: rgba(0, 255, 0, 0.10);
				/* box-shadow: 5px 5px 10px rgba(0, 0, 0, 0.20); */
			}
			.zmi-translate-element-id {
				color:white;
				position: absolute;
				margin:-4px;
				min-width: 6rem;
				padding: 0 1px 0 .2rem;
			}
			.zmi-translate-element-id a {
				color:white !important;
				display:inline-block;
				padding:0 3px;
			}
			.zmi-translate-element-id i {
				cursor: pointer;
				float: right;
				display: inline-block;
				margin: 0;
				height: 1.25rem;
				background: rgb(0 0 0 / 22%);
				width: 1.5rem;
				text-align: center;
				padding: 0.25rem 0 0;
			}
			.zmi-translate-element-id i:hover {
				background: rgb(0 0 0 / 100%);
			}
			td.zmi-translate-left .zmi-translate-element-id {
				background-color: #28a745;
			}
			td.zmi-translate-right .zmi-translate-element-id {
				background-color: red;
			}
			.zmi-translate-right {
				padding:4px;
				background-color: rgba(255, 0, 0, 0.10);
			}
			.zmi-translate-right.bg-alert {
				background-color:#CCCCCC;
			}
			.zmi-translate-element {
				margin:6px 12px 6px 6px;
			}
			.zmi-translate-element .row {
				margin:0 !important;
			}
			td.zmi-translate-left {
				border: 1px solid darkgreen;
			}
			td.zmi-translate-right {
				border: 1px solid red !important;
			}
			.zmiRenderShort {
				width:350px !important;
				margin-top:1.5em;
			}
			body.maximized .zmiRenderShort {
				width:auto !important;
			}
			.ui-widget-overlay {
				opacity: 0.2;
			}
			#google_translate_element,
			select.lang {
				float:right;
				margin:.3em;
			}
			.skiptranslate iframe {
				min-height: 2.7rem;
				background: #fff;
				padding-top: .15rem;
			}
			.zmi figure img {
				max-width: min(calc(50vw - 56px), 460px);
				height: auto;
			}
		</style>
	'''


def renderScripts():
	"""Render JavaScript code"""
	return '''
		<script>
			function save(sender) {
				var $container_div = $($(sender).closest('td').find('.zmi-translate-element'));
				// var $container_div = $($(sender).parents("div")[0]);
				// var $rendershort_div = $("div.zmiRenderShort div.contentEditable",$container_div);
				// var $rendershort_div = $($(sender)).parent().next();
				var $rendershort_div = $container_div.children('.zmiRenderShort')[0];
				console.log($rendershort_div);
			
				var id = $($rendershort_div).attr("id");
				id = id.substring(id.indexOf("_")+1);
				id = id.substring(0,id.lastIndexOf("_"));
				console.log('ID = '+id)
			
				var lang = $($rendershort_div).attr("id");
				lang = lang.substring(lang.lastIndexOf("_")+1);
				console.log('LANG = '+lang)
			
				var html = $('div#'+id, $rendershort_div).html();
				var text = html; //$($rendershort_div).text();

				// Removing HTML artefacts from Translator-JS or ZMI
				text = text.replace(/<font(.*?)>|<\\/font(.*?)>/gi,'');
				text = text.replace(/<\\/font(.*?)>/gi,'');
				text = text.replace(/<span class=\\"unicode\\">(.*?)<\\/span>/gi,'');

				// Let browser fix/normalize html
				const parser = new DOMParser();
				const doc = parser.parseFromString(text, "text/html");
				text = doc.body.innerHTML;
				console.log('TEXT = ' +text)
				if (confirm("Save (Automatic Pre-) Translation?\\n\\n"+text)) {
					$($container_div).addClass('bg-alert');
					var params = {};
					params['lang'] = lang;
					params['text_'+lang] = text;
					$.post(id+'/manage_changeProperties',params,function(data){
						$($container_div).removeClass('bg-alert');
					},'html');
				}
			}
			$ZMI.registerReady(function() {
				$('.zmiRenderShort .contentEditable').off('click');
				$('.zmiRenderShort [onclick]').removeAttr('onclick');
				$('.zmiRenderShort [ondblclick]').removeAttr('ondblclick');
				$('.zmiRenderShort span.unicode').remove();
			});
		</script>
	'''


#################################################
# MAIN
#################################################
def manage_translate(self):
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

