//++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
//+++ Ajax.org Cloud9 Editor
//+++ http://ace.ajax.org
//+++ @see $ZMS_HOME/plugins/www/ace.ajax.org
//++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
$(function(){
	if ($("textarea#text").length == 0) {
		$("#editor").hide();
	}
	else {
		var dom = require("ace/lib/dom");
		// add command to all new editor instances
		require("ace/commands/default_commands").commands.push({
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
		$("textarea#text").hide();
		editor = ace.edit("editor");
		var value = $("textarea#text").val();
		var content_type = $("input#content_type").val();
		if (typeof content_type == "undefined" || content_type == null || content_type == '' || content_type == 'text/x-unknown-content-type') {
			var absolute_url = $("span#absolute_url").text();
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
		if (value.indexOf("<html") == 0) {
			content_type = "text/html";
		}
		if (value.indexOf("<?xml") == 0 || value.indexOf("tal:") >= 0) {
			content_type = "text/xml";
		}
		if (value.indexOf("#!/usr/bin/python") == 0 || value.indexOf("## Script (Python)") == 0) {
			content_type = "python";
		}
		var mode = "text";
		if (content_type == "text/html") {
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
		editor.setTheme("ace/theme/chrome");
		editor.getSession().setMode('ace/mode/'+mode);
		editor.getSession().setValue(value);
		editor.getSession().on("change",function() {
			$("textarea#text").val(editor.getSession().getValue()).change();
		});
	}
});
