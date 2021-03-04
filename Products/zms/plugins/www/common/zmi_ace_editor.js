//++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
//+++ Ajax.org Cloud9 Editor
//+++ http://ace.ajax.org
//+++ @see $ZMS_HOME/plugins/www/ace.ajax.org
//++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
$(function(){
	$(".zmi-ace-editor").each(function() {
		var dom = ace.require("ace/lib/dom");
		// add command to all new editor instances
		ace.require("ace/commands/default_commands").commands.push({
			name: "Toggle Fullscreen",
			bindKey: "F10",
			exec: function(editor) {
				var fullScreen = dom.toggleCssClass(document.body, "fullScreen")
				dom.setCssClass(editor.container, "fullScreen", fullScreen)
				editor.setAutoScrollEditorIntoView(!fullScreen)
				editor.resize()
			}
		});
		// @see https://github.com/ajaxorg/ace/wiki/Embedding---API
		var $textarea = $(".form-control-ace-editor",this);
		if ($textarea.is(":visible")) {
			$textarea.hide();
			var name = $textarea.attr("name");
			var value = $textarea.val();
			var editor = ace.edit("editor_"+name);
			var content_type = $("input#content_type",this).val();
			if ( $textarea.attr('data-content_type') ) {
				content_type = $textarea.attr('data-content_type');
			}
			if (typeof content_type == "undefined" || content_type == null || content_type == '' || content_type == 'text/x-unknown-content-type') {
				var absolute_url = $(".control-label-ace-editor a",this).attr("href");
				absolute_url = absolute_url.substr(0,absolute_url.lastIndexOf("/")); // strip manage_main
				var id = absolute_url.substr(absolute_url.lastIndexOf("/")+1);
				if (id.endsWith(".css")) {
					content_type = "text/css";
				}
				else if (id.endsWith(".less")) {
					content_type = "text/less";
				}
				else if (id.endsWith(".js")) {
					content_type = "text/javascript";
				}
				else {
					content_type = "text/html";
				}
			}
			if ( 0 === value.indexOf("<html") && content_type != 'dtml') {
				content_type = "text/html";
			}
			if ( 0 === value.indexOf("<?xml") || value.indexOf("tal:") >= 0) {
				content_type = "text/xml";
			}
			if ( 0 === value.indexOf("#!/usr/bin/python") || 0 === value.indexOf("## Script (Python)") ) {
				content_type = "python";
			}
			var mode = "text";
			if (content_type == "html" || content_type == "text/html") {
				mode = "html";
			}
			else if (content_type == "text/css" || content_type == "application/css" || content_type == "application/x-css") {
				mode = "css";
			}
			else if (content_type == "text/less") {
				mode = "less";
			}
			else if (content_type == "text/javascript" || content_type == "application/javascript" || content_type == "application/x-javascript") {
				mode = "javascript";
			}
			else if (content_type == "text/xml") {
				mode = "xml";
			}
			else if (content_type == "python") {
				mode = 'python';
			}
			else if (content_type == "sql") {
				mode = 'sql';
			}
			else if (content_type == "json") {
				mode = 'json';
			}
			else if (content_type == "dtml") {
				mode = 'markdown';
			}
			editor.setTheme("ace/theme/eclipse");
			editor.getSession().setMode('ace/mode/'+mode);
			editor.getSession().setValue(value);
			editor.getSession().on("change",function() {
				$textarea.val(editor.getSession().getValue()).change();
			});
		}
	});
});
