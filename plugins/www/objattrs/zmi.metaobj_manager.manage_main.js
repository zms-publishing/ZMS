function html_quote(s) {
	var q = s.replace(/\</gi,'&lt;');
	q = '<textarea class="form-fixed" cols="80" rows="' + q.split('\n').length + '">' + q + '</textarea>';
	return q;
}

function zmiToggleTextarea(span) {
	var textarea = $(span).prev("textarea");
	var rows = 1;
	var wrap = 'virtual';
	if ($(textarea).prop("rows")==rows) {
		rows = 10;
		wrap = 'off';
	}
	$(textarea).prop({rows:rows,wrap:wrap}).css({height:rows*20});
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
		html += html_quote('<img tal:attributes="src python:zmscontext.attr(\'' + id + '\').getHref(request)"/>');
	}
	else if (type == 'file') {
		html += html_quote('<a tal:attributes="href python:zmscontext.attr(\'' + id + '\').getHref(request)"></a>');
	}
	else {
		html += html_quote('<tal:block tal:content="structure python:zmscontext.attr(\'' + id + '\')">the ' + id + '</tal:block>');
	}
	$('#zmiPopup').html(html);
	showFancybox({
			'href':'#zmiPopup',
			'autoDimensions':true,
			'transitionIn':'fade',
			'transitionOut':'fade'
		});
}

