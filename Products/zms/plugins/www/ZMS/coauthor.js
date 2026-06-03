(function(window, $) {
	'use strict';

	function isManageCoauthorPage() {
		var body = document.body;
		if (!body) {
			return false;
		}
		if (body.classList && body.classList.contains('manage_coauthor')) {
			return true;
		}
		return !!document.getElementById('manage_coauthor_grid');
	}

	function clearGlobalHooks() {
		try { delete window.switchLanguage; } catch (e) { window.switchLanguage = undefined; }
		try { delete window.switchCoauthorMode; } catch (e) { window.switchCoauthorMode = undefined; }
		try { delete window.triggerAutoTranslate; } catch (e) { window.triggerAutoTranslate = undefined; }
		try { delete window.googleTranslateElementInit; } catch (e) { window.googleTranslateElementInit = undefined; }
	}

	function initGoogleTranslateElementWhenReady() {
		if (!$('#google_translate_element').length) {
			return;
		}
		var retries = 0;
		var maxRetries = 30;
		var timer = window.setInterval(function() {
			retries++;
			if (window.google && window.google.translate) {
				window.clearInterval(timer);
				googleTranslateElementInit();
				return;
			}
			if (retries >= maxRetries) {
				window.clearInterval(timer);
			}
		}, 200);
	}

	function getTranslateLanguages() {
		return {
			lang1: $('select[name="lang1"]').val(),
			lang2: $('select[name="lang2"]').val()
		};
	}

	function getAiFeatureSettings() {
		var node = document.getElementById('manage_coauthor_grid');
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
		var settings = getAiFeatureSettings();
		var sameLanguage = langs.lang1 === langs.lang2;
		var $button = getAutoActionButton();
		if (!$button.length) {
			return;
		}
		if (sameLanguage) {
			$button.text('Auto-Editing');
			$button.attr('title', settings.aiEnabled
				? 'Improve text quality and complete missing metadata using the configured LLM service.'
				: 'Auto-Editing requires a configured ZMSLLMConnector.');
			$button.prop('disabled', !settings.aiEnabled);
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

		var contextContent = '';
		$.ajax({
			type: 'GET',
			url: $ZMI.get_rest_api_url(getAiFeatureSettings().contextUrl) + '/get_body_content',
			dataType: 'text',
			data: { lang: getZMILang() },
			async: false,
			success: function(data) {
				if (data) {
					contextContent = data;
				}
			}
		});
		contextContent = contextContent.replace(/\s+/g, ' ').trim();
		contextContent = contextContent.replace(/<[^>]*>/g, '');
		contextContent = contextContent.replace(/&[^;]+;/g, '');
		if (contextContent.length > 5000) {
			contextContent = contextContent.substring(0, 5000);
		}
		payload.context_content = contextContent;

		return [
			'You are a CMS editorial assistant working in same-language editing mode.',
			'Return only valid JSON and no markdown.',
			'JSON schema: {"fields": {"<field_id>": "<suggested text>"}}',
			'Keep the language exactly as ' + targetLang + '.',
			'Improve clarity, grammar, style, and consistency without changing the factual meaning.',
			'Do not invent facts, numbers, names, or claims that are not supported by the input.',
			'The context_content shall be used to derive missing or weak metadata fields.' +
			(metadataEnabled
				? 'Fill missing or weak metadata fields when they can be derived from the existing content.'
				: 'Do not generate extra metadata beyond clear text improvements.'),
			'Omit any field that should stay unchanged.',
			'Input JSON:',
			JSON.stringify(payload, null, 2)
		].join('\n');
	}

	function requestHtmlDiff(originalText, changedText) {
		var settings = getAiFeatureSettings();
		return $.ajax({
			type: 'POST',
			url: $ZMI.get_rest_api_url(settings.contextUrl) + '/get_htmldiff',
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

	function renderAutoEditDiff(row, diffHtml) {
		var $target = row.targetInput;
		var isInline = $target.is('input.form-control.datatype-11');
		var $wrapper = $('<div class="ai-diff-wrapper"></div>');
		var editorClass = isInline ? 'ai-diff-editor ai-diff-editor-inline' : 'ai-diff-editor';
		var $editor = $('<div></div>').addClass(editorClass).html(diffHtml || '');
		$wrapper.append($editor);
		$wrapper.append($('<div class="ai-diff-hint"></div>').text('Click green additions to reject them. Click red deletions to restore them.'));
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
		if (!plainTextMode) {
			return $clone.html();
		}
		$clone.find('br').replaceWith('\n');
		$clone.find('p,div,li,tr,h1,h2,h3,h4,h5,h6').each(function() {
			$(this).append('\n');
		});
		return $clone.text().replace(/\n{3,}/g, '\n\n');
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
			return updated;
		});
	}

	function runSameLanguageAutoEdit() {
		var settings = getAiFeatureSettings();
		if (!settings.aiEnabled) {
			alert('Auto-Editing requires a configured ZMSLLMConnector.');
			return;
		}
		var langs = getTranslateLanguages();
		var rows = collectAutoEditRows();
		if (!rows.length) {
			alert('No editable text fields found.');
			return;
		}
		var prompt = buildAutoEditPrompt(rows, langs.lang1, langs.lang2, settings.metadataEnabled);
		showTranslateProgress('Auto-editing content...');
		$.ajax({
			url: $ZMI.get_rest_api_url(settings.contextUrl) + '/llm_chat',
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
				alert('Auto-Editing completed for ' + updated + ' field(s).');
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

	function switchLanguage(langKey, langValue) {
		var url = new URL(window.location);
		url.searchParams.set(langKey, langValue);
		window.location.href = url.toString();
	}

	function switchCoauthorMode(mode) {
		var url = new URL(window.location);
		url.searchParams.set('coauthor_mode', mode);
		window.location.href = url.toString();
	}

	function googleLangCode(lang) {
		var map = {
			ger: 'de',
			eng: 'en',
			fra: 'fr',
			ita: 'it',
			spa: 'es',
			rus: 'ru',
			tur: 'tr'
		};
		return map[lang] || 'en';
	}

	function translateText(sourceLang, targetLang, text, callback) {
		if (!text || $.trim(text) === '') {
			callback(text);
			return;
		}
		var url = 'https://translate.googleapis.com/translate_a/single?client=gtx&sl=' + sourceLang + '&tl=' + targetLang + '&dt=t&q=' + encodeURIComponent(text);
		fetch(url)
			.then(function(response) { return response.json(); })
			.then(function(data) {
				if (data && data[0]) {
					callback(data[0].map(function(item) { return item[0]; }).join(''));
				}
				else {
					callback(text);
				}
			})
			.catch(function() {
				callback(text);
			});
	}

	function translateAndCopy() {
		var langs = getTranslateLanguages();
		var sourceLang = googleLangCode(langs.lang1);
		var targetLang = googleLangCode(langs.lang2);
		var totalFields = 0;
		var processedFields = 0;
		$('.form-group-row').each(function() {
			var $row = $(this);
			var $leftInput = getEditableField($row.find('.zmi-translate-left'));
			var $rightInput = getEditableField($row.find('.zmi-translate-right'));
			if ($leftInput.length && $rightInput.length) {
				totalFields++;
			}
		});
		if (!totalFields) {
			alert('No translatable fields found.');
			return;
		}
		showTranslateProgress('Translating... 0/' + totalFields);
		$('.form-group-row').each(function() {
			var $row = $(this);
			var $leftInput = getEditableField($row.find('.zmi-translate-left'));
			var $rightInput = getEditableField($row.find('.zmi-translate-right'));
			if (!$leftInput.length || !$rightInput.length) {
				return;
			}
			translateText(sourceLang, targetLang, $leftInput.val() || '', function(translatedText) {
				$rightInput.val(translatedText);
				$rightInput.css('background-color', '#ffffcc');
				processedFields++;
				showTranslateProgress('Translating... ' + processedFields + '/' + totalFields);
				if (processedFields >= totalFields) {
					hideTranslateProgress();
				}
			});
		});
	}

	function googleTranslateElementInit() {
		var langs = getTranslateLanguages();
		var sourceLang = googleLangCode(langs.lang1);
		var targetLang = googleLangCode(langs.lang2);
		if (!window.google || !window.google.translate || !$('#google_translate_element').length) {
			return;
		}
		new window.google.translate.TranslateElement({
			pageLanguage: sourceLang,
			includedLanguages: targetLang,
			layout: window.google.translate.TranslateElement.InlineLayout.SIMPLE,
			autoDisplay: false
		}, 'google_translate_element');
	}

	function triggerAutoTranslate() {
		var langs = getTranslateLanguages();
		if (langs.lang1 === langs.lang2) {
			if (window.confirm('This will improve text quality and complete missing metadata in ' + langs.lang2 + '. Continue?')) {
				runSameLanguageAutoEdit();
			}
			return;
		}
		if (window.confirm('This will copy and translate content from ' + langs.lang1 + ' to ' + langs.lang2 + '. Continue?')) {
			translateAndCopy();
		}
	}

	// if (!isManageCoauthorPage()) {
	// 	clearGlobalHooks();
	// 	return;
	// }

	$ZMI.registerReady(function() {
		$('[data-toggle="tooltip"]').tooltip();
		updateAutoActionButton();
		initGoogleTranslateElementWhenReady();

		$(document).off('change.coauthorLang').on('change.coauthorLang', 'select.lang[data-lang-key]', function() {
			switchLanguage($(this).data('lang-key'), $(this).val());
		});

		$(document).off('click.coauthorMode').on('click.coauthorMode', '[data-coauthor-mode]', function(e) {
			e.preventDefault();
			switchCoauthorMode($(this).data('coauthor-mode'));
		});

		$(document).off('click.coauthorAuto').on('click.coauthorAuto', '[data-coauthor-action="auto-translate"]', function(e) {
			e.preventDefault();
			triggerAutoTranslate();
		});

		$(document).off('click.coauthorRow').on('click.coauthorRow', '.clickable-row[data-url]', function(e) {
			if ($(e.target).closest('a, button, input, select, textarea, label, .ai-diff-editor').length) {
				return;
			}
			var url = $(this).data('url');
			if (url) {
				window.location.href = url;
			}
		});

		$('form.translate-forms').on('submit', function() {
			commitAutoEditDiffEditors();
			$('#translate_lang').val($('select[name="lang2"]').val());
		});

		$(document).off('click.aiDiffToggle').on('click.aiDiffToggle', '.ai-diff-editor ins, .ai-diff-editor del', function(e) {
			e.preventDefault();
			e.stopPropagation();
			toggleDiffToken($(this));
		});

		$('.zmi-translate-left input, .zmi-translate-left textarea, .zmi-translate-left select').prop('disabled', true);
		$('.zmi-translate-left input, .zmi-translate-left textarea, .zmi-translate-left select').css('background-color', '#f8f9fa');

		$('.zmi.manage_coauthor div.contentEditable').each(function() {
			$(this).replaceWith($(this).html());
		});
	});
})(window, window.jQuery);
