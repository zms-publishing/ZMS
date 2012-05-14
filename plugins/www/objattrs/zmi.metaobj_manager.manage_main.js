function html_quote(s) {
	var q = s.replace(/\</gi,'&lt;');
	q = '<textarea class="form-fixed" cols="80" rows="' + q.split('\n').length + '">' + q + '</textarea>';
	return q;
}

function zmiToggleTextarea(span) {
	var textarea = $(span).prev("textarea");
	var rows = 1;
	if ($(textarea).prop("rows")==rows) {
		rows = 10;
	}
	$(textarea).prop({rows:rows,wrap:'off'}).css({height:rows*20});
}

function zmiShowHint(id, type) {
	if ($('#zmiPopup').length==0) {
		var html = '';
		html += '<div style="display:none">';
		html += '<div id="zmiPopup" class="ui-state-highlight ui-corner-all" style="padding: 1em;">';
		html += '</div>';
		html += '</div>';
		$('body').append(html);
	}
	var html = '';
	if (type == 'image') {
		html += ''
			+ '<div class="form-label"><img src="/misc_/PageTemplates/zpt.gif"/> TAL</div>'
			+ html_quote('<img tal:attributes="src python:zmscontext.attr(\'' + id + '\').getHref(request)"/>')
			+ '<div class="form-label"><img src="/misc_/OFSP/dtmlmethod.gif"/> DTML</div>'
			+ html_quote('<img src="<dtml-var "attr(\'' + id + '\').getHref(REQUEST)">"/>')
			;
	}
	else if (type == 'file') {
		html += ''
			+ '<div class="form-label"><img src="/misc_/PageTemplates/zpt.gif"/> TAL</div>'
			+ html_quote('<a tal:attributes="href python:zmscontext.attr(\'' + id + '\').getHref(request)"></a>')
			+ '<div class="form-label"><img src="/misc_/OFSP/dtmlmethod.gif"/> DTML</div>'
			+ html_quote('<a href="<dtml-var "attr(\'' + id + '\').getHref(REQUEST)">"></a>')
			;
	}
	else {
		html += ''
			+ '<div class="form-label"><img src="/misc_/PageTemplates/zpt.gif"/> TAL</div>'
			+ html_quote('<tal:block tal:content="structure python:zmscontext.attr(\'' + id + '\')">the ' + id + '</tal:block>')
			+ '<div class="form-label"><img src="/misc_/OFSP/dtmlmethod.gif"/> DTML</div>'
			+ html_quote('<dtml-var "attr(\'' + id + '\')">')
			;
	}
	$('#zmiPopup').html(html);
	showFancybox({
			'href':'#zmiPopup',
			'autoDimensions':true,
			'transitionIn':'fade',
			'transitionOut':'fade'
		});
}

