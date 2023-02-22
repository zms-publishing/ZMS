//++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
//+++ ACE Cloud9 Editor
//+++ https://ace.c9.io/
//+++ @see $ZMS_HOME/plugins/www/ace.ajax.org
//++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

function show_ace_editor(e, toggle=false) {

	if ( toggle == false ) {
		var $textarea = $('textarea',$(e));
		var editor_id = 'editor_' + $textarea.attr('id');
	} else {
		var $textarea = $(e);
		var editor_id = 'editor_' + $textarea.attr('id');
		if ( $(e).closest('td').find('#'+editor_id).length > 0 ) {
			// Avoid stacking multiple editors 
			return;
		};
		var zopeurl = $(e).attr('data-zopeurl');
		$textarea.addClass('form-control-ace-editor');
		$textarea.parent().addClass('zmi-ace-editor')
		$textarea.after('<div id="' + editor_id + '">ace editor text</div>');
		$textarea.closest('td').append('<div class="control-label-ace-editor"><div><i onclick="remove_ace_editor(\'' + editor_id + '\')" title="Close Editor" class="close fas fa-chevron-up text-primary"></i></div><div><a title="Zope-Object-Editor" target="_blank" href="' + zopeurl + '">' + $textarea.attr('id').split('attr_custom_')[1] + '</a></div></div>');
	}

	var dom = ace.require('ace/lib/dom');
	// add command to all new editor instances
	ace.require('ace/commands/default_commands').commands.push({
		name: 'Toggle Fullscreen',
		bindKey: 'F10',
		exec: function(editor) {
			var fullScreen = dom.toggleCssClass(document.body, 'fullScreen')
			dom.setCssClass(editor.container, 'fullScreen', fullScreen)
			editor.setAutoScrollEditorIntoView(!fullScreen)
			editor.resize()
		}
	});

	// @see https://github.com/ajaxorg/ace/wiki/Embedding---API
	if ($textarea.is(':visible')) {
		$textarea.hide();
		var value = $textarea.val();
		var editor = ace.edit(editor_id);
		var content_type = $('input.content_type',$(e).parent()).val();
		if ( $textarea.attr('data-content_type') ) {
			content_type = $textarea.attr('data-content_type');
		}
		if (typeof content_type == 'undefined' || content_type == null || content_type == '' || content_type == 'text/x-unknown-content-type') {
			var absolute_url = $('.control-label-ace-editor a',this).attr('href');
			absolute_url = absolute_url.substr(0,absolute_url.lastIndexOf('/')); // strip manage_main
			var id = absolute_url.substr(absolute_url.lastIndexOf('/')+1);
			if (id.endsWith('.css')) {
				content_type = 'text/css';
			}
			else if (id.endsWith('.less')) {
				content_type = 'text/less';
			}
			else if (id.endsWith('.js')) {
				content_type = 'text/javascript';
			}
			else {
				content_type = 'text/html';
			}
		}
		if ( ( 0 === value.indexOf('<html') ||  0 === value.indexOf('<!DOCTYPE html>') ) && content_type != 'dtml') {
			content_type = 'text/html';
		}
		if ( 0 === value.indexOf('<?xml') || value.indexOf('tal:') >= 0) {
			content_type = 'text/xml';
		}
		if ( 0 === value.indexOf('#!') || 0 === value.indexOf('##') || content_type=='External Method' || content_type=='Python Script' ) {
			content_type = 'python';
		}
		var mode = 'text';
		if (content_type == 'html' || content_type == 'text/html') {
			mode = 'html';
		}
		else if (content_type == 'text/css' || content_type == 'application/css' || content_type == 'application/x-css') {
			mode = 'css';
		}
		else if (content_type == 'text/less') {
			mode = 'less';
		}
		else if (content_type == 'text/javascript' || content_type == 'application/javascript' || content_type == 'application/x-javascript') {
			mode = 'javascript';
		}
		else if (content_type == 'text/xml') {
			mode = 'xml';
		}
		else if (content_type == 'python') {
			mode = 'python';
		}
		else if (content_type == 'sql' || content_type=='Z SQL Method') {
			mode = 'sql';
		}
		else if (content_type == 'json') {
			mode = 'json';
		}
		else if (content_type == 'dtml') {
			mode = 'markdown';
		}
		editor.setTheme('ace/theme/eclipse');
		editor.getSession().setMode('ace/mode/'+mode);
		editor.getSession().setValue(value);
		editor.getSession().setOptions({ tabSize: 4, useSoftTabs: false });
		editor.getSession().on('change',function() {
			$textarea.val(editor.getSession().getValue()).change();
		});
	}
}

function remove_ace_editor(id) {
	var $ace = $('#' + id);
	var $ace_td = $ace.closest('td');
	$('.zmi-code', $ace_td).removeClass('zmi-ace-editor');
	$('.control-label-ace-editor', $ace_td).remove();
	ace.edit(id).destroy();
	$('#' + id).animate({height: 0},600, 
		function () {
			$('#' + id).remove();
			$('.zmi-code textarea', $ace_td).show();
		}
	);
}

$(function(){
	$('.zmi-ace-editor').each(function() {
		show_ace_editor( $(this), toggle=false );
	});
});
