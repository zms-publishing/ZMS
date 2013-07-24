// ############################################################################
// ### Common
// ############################################################################

/**
 * Open link in iframe (jQuery UI Dialog).
 */
function zmiIframe(href, data, opt) {
	if ($('#zmiIframe').length==0) {
		$('body').append('<div id="zmiIframe"></div>');
	}
	$.get( href, data, function(result) {
			var $result = $(result);
			if ($("div#system_msg",$result).length>0) {
				var manage_tabs_message = $("div#system_msg",$result).text();
				manage_tabs_message = manage_tabs_message.substr(0,manage_tabs_message.lastIndexOf("("));
				var href = self.location.href;
				href = href.substr(0,href.indexOf("?"))+"?lang="+getZMILang()+"&manage_tabs_message="+manage_tabs_message;
				self.location.href = href;
			}
			else {
				opt["modal"] = true;
				opt["height"] = "auto";
				opt["width"] = "auto";
				$('#zmiIframe').html(result);
				var title = $('#zmiIframe div.zmi').attr("title");
				if (typeof title != "undefined" && title) {
					opt["title"] = title;
				}
				initUI($('#zmiIframe')).dialog(opt);
			}
		});
}

/**
 * Max-/Minimize ZMI.
 */
function zmiToggleMaximize() {
	toggleCookie('zmi_maximized');
	$('body').toggleClass('maximized');
}

/**
 * Un-/select checkboxes.
 */
function selectCheckboxes(fm, v) {
	if (typeof v == 'undefined') {
		v = !$(':checkbox:not([name~=active])',fm).prop('checked');
	}
	$(':checkbox:not([name~=active])',fm).prop('checked',v)
}

// ############################################################################
// ### Forms
// ############################################################################

var zmiSortableRownum = null;

$(function(){
	// !!! Important: sortable() depends on JQuery UI !!!
	var sortableTables = $("table.zmi-sortable > tbody");
	if (sortableTables.length > 0) {
		// Sort (Move Up/Down)
		var fixHelper = function(e, ui) { // Return a helper with preserved width of cells
			ui.children().each(function() {
				$(this).width($(this).width());
			});
			return ui;
		};
		$("table.zmi-sortable > tbody").sortable({
				helper:fixHelper,
				forcePlaceholderSize:true,
				placeholder:'ui-state-highlight',
				handle:'.zmiContainerColLeft img.grippy',
				start: function(event, ui) {
					var trs = $('table.zmi-sortable > tbody > tr');
					var i = 0;
					for (i = 0; i < trs.length; i++) {
						if ( $(trs[i]).attr('id')==ui.item.attr('id')) {
							break;
						}
					}
					zmiSortableRownum = i;
				},
				stop: function(event, ui) {
					var trs = $('table.zmi-sortable > tbody > tr');
					var i = 0;
					for (i = 0; i < trs.length; i++) {
						if ( $(trs[i]).attr('id')==ui.item.attr('id')) {
							break;
						}
					}
					if ( zmiSortableRownum != i) {
						var id = ui.item.attr('id');
						id = id.substr(id.indexOf('_')+1);
						var href = id+'/manage_moveObjToPos?lang='+getZMILang()+'&pos:int='+(i+1)+'&fmt=json';
						$.get(href,function(result){
							var system_msg = eval('('+result+')');
							$('#system_msg').html(system_msg).show('normal');
							setTimeout(function(){$('#system_msg').hide('normal')},5000);
						});
					}
					zmiSortableRownum = null;
				}
			});
	}
	// Form-Elements
	$("select.form-element,input.form-element,textarea.form-element,select.form-small,input.form-small,textarea.form-small")
		.focus( function(evt) {$(this).addClass("form-element-focused"); })
		.blur( function(evt) { $(this).removeClass("form-element-focused"); })
	;
	// Action-Lists
	$("input.zmi-ids-list:checkbox").click( function(evt) { zmiActionButtonsRefresh(this,evt); } );
	$("select.zmi-action")
		.focus( function(evt) { zmiActionPopulate(this); })
		.mouseover( function(evt) { zmiActionPopulate(this); })
		;
	$('.ui-accordion h3').click( function(evt) {
		var $container = $(this);
		var $icon = $('span:first',$container);
		var $content = $('.ui-accordion-content',$(this).parents('div')[0]);
		if ($container.hasClass('ui-state-active')) {
			$content.hide('normal');
		}
		else {
			$content.show('normal');
		}
		$container.toggleClass('ui-state-active').toggleClass('ui-state-default');
		$icon.toggleClass('ui-icon-triangle-1-s').toggleClass('ui-icon-triangle-1-e');
		//$content.toggleClass('ui-accordion-content-active');
		var zmi_form_section_id = $container.attr('id');
		if (typeof zmi_form_section_id != 'undefined') {
			toggleCookie(zmi_form_section_id+'_collapsed');
		}
	});

	// Sitemap Button
	var $btn_sitemap = $('#ZMIManageTabsBar li.icon-sitemap');
	if ($btn_sitemap.length > 0) {
		var $a = $('#ZMIManageTabsBar li.icon-sitemap a');
		if (self.window.parent.frames.length > 1 && typeof self.window.parent != "undefined" && (self.window.parent.location+"").indexOf('dtpref_sitemap=1') > 0) {
			$a.attr('target','_parent');
			$a.attr('href',$a.attr('href')+'&dtpref_sitemap=0');
			$btn_sitemap.addClass('on');
		}
		else {
			$a.attr('href',$a.attr('href')+'&dtpref_sitemap=1');
			$btn_sitemap.removeClass('on');
		}
	}

});

// #############################################################################
// ### ZMI Pathcropping
// #############################################################################


function zmiRelativateUrl(path, url) {
	var protocol = self.location.href;
	protocol = protocol.substr(0,protocol.indexOf(":")+3);
	var server_url = self.location.href;
	server_url = server_url.substr(protocol.length);
	server_url = protocol + server_url.substr(0,server_url.indexOf("/"));
	var currntPath = null;
	if (path.indexOf(server_url)==0) {
		currntPath = path.substr(server_url.length+1);
	}
	else if (path.indexOf('/')==0) {
		currntPath = path.substr(1);
	}
	var targetPath = null;
	if (url.indexOf(server_url)==0) {
		targetPath = url.substr(server_url.length+1);
	}
	else if (url.indexOf('/')==0) {
		targetPath = url.substr(1);
	}
	if (currntPath == null || targetPath == null) {
		return url;
	}
	while ( currntPath.length > 0 && targetPath.length > 0) {
		var i = currntPath.indexOf( '/');
		var j = targetPath.indexOf( '/');
		if ( i < 0) {
			currntElmnt = currntPath;
		}
		else {
			currntElmnt = currntPath.substring( 0, i);
		}
		if ( j < 0) {
			targetElmnt = targetPath;
		}
		else {
			targetElmnt = targetPath.substring( 0, j);
		}
		if ( currntElmnt != targetElmnt) {
			break;
		}
		if ( i < 0) {
			currntPath = '';
		}
		else {
			currntPath = currntPath.substring( i + 1);
		}
		if ( j < 0) {
			targetPath = '';
		}
		else {
			targetPath = targetPath.substring( j + 1);
		}
	}
	while ( currntPath.length > 0) {
		var i = currntPath.indexOf( '/');
		if ( i < 0) {
			currntElmnt = currntPath;
			currntPath = '';
		}
		else {
			currntElmnt = currntPath.substring( 0, i);
			currntPath = currntPath.substring( i + 1);
		}
		targetPath = '../' + targetPath;
	}
	url = './' + targetPath;
	return url;
}

function zmiRelativateUrls(s,page_url) {
	var splitTags = ['<a href="','<img src="'];
	for ( var h = 0; h < splitTags.length; h++) {
	var splitTag = splitTags[h];
		var vSplit = s.split(splitTag);
		var v = vSplit[0];
		for ( var i = 1; i < vSplit.length; i++) {
			var j = vSplit[i].indexOf('"');
			var url = vSplit[i].substring(0,j);
			if (url.indexOf('./')<0) {
				url = zmiRelativateUrl(page_url,url);
			}
			v += splitTag + url + vSplit[i].substring(j);
		}
		s = v;
	}
	return s;
}

// #############################################################################
// ### ZMI Auto-Save
// #############################################################################

function confirmChanges(el) {
	if (el && self.name == 'cameFromForm') {
		el.target = '_parent';
	}
	if (navigator.platform.indexOf("Mac")<0) {
		var anyFormModified = false;
		for (i=0; i<document.forms.length; i++) {
			anyFormModified |= isFormModified(document.forms[i]);
		}
		if ( anyFormModified) {
			if (!confirm(getZMILangStr('MSG_CONFIRM_DISCARD_CHANGES'))) {
				return false;
			}
		}
	}
	return true;
}


// #############################################################################
// ### ZMI Action-Lists
// #############################################################################

var zmiActionPrefix = 'select_actions_';

/**
 * Get descendant languages.
 */
function zmiGetDescendantLanguages() {
	var base = self.location.href;
	base = base.substr(0,base.lastIndexOf('/'));
	var langs = eval('('+$.ajax({
		url: base+'/getDescendantLanguages',
		data:{id:getZMILang()},
		datatype:'text',
		async: false
		}).responseText+')');
	if (langs.length > 1) {
		var labels = '';
		for ( var i = 0; i < langs.length; i++) {
			if (labels.length>0) {
				labels += ', ';
			}
			labels += $.ajax({
				url: 'getLanguageLabel',
				data:{id:langs[i]},
				datatype:'text',
				async: false
				}).responseText;
		}
		return ' '+getZMILangStr('MSG_CONFIRM_DESCENDANT_LANGS').replace("%s",langs);
	}
	return '';
}

/**
 * Confirm execution of action from select.
 *
 * @param fm
 * @param target
 * @param label
 */
function zmiConfirmAction(fm, target, label) {
	var b = true;
	var i = $("input[name='ids:list']:checkbox").length;
	if (target.indexOf("../") == 0) {
		i = 1;
	}
	if (target.indexOf("manage_rollbackObjChanges") >= 0) {
		b = confirm(getZMILangStr('MSG_ROLLBACKVERSIONCHANGES'));
	}
	else if (target.indexOf("manage_cutObjects") >= 0) {
		var msg = getZMILangStr('MSG_CONFIRM_CUTOBJS');
		msg = msg.replace("%i",""+i);
		msg += zmiGetDescendantLanguages();
		b = i > 0 && confirm(msg);
	}
	else if (target.indexOf("manage_eraseObjs") >= 0) {
		var msg = getZMILangStr('MSG_CONFIRM_DELOBJS');
		msg = msg.replace("%i",""+i);
		b = i > 0 && confirm(msg);
	}
	else if (target.indexOf("manage_deleteObjs") >= 0) {
		var msg = getZMILangStr('MSG_CONFIRM_TRASHOBJS');
		msg = msg.replace("%i",""+i);
		msg += zmiGetDescendantLanguages();
		b = i > 0 && confirm(msg);
	}
	else if (target.indexOf("manage_undoObjs") >= 0) {
		var msg = getZMILangStr('MSG_CONFIRM_DISCARD_CHANGES');
		msg = msg.replace("%i",""+i);
		b = i > 0 && confirm(msg);
	}
	else if (target.indexOf("manage_executeMetacmd") >=0 ) {
		var description = $.ajax({
			url: 'getMetaCmdDescription',
			data:{name:label},
			datatype:'text',
			async: false
			}).responseText;
		if (typeof description != 'undefined' && description.length > 0) {
			b = confirm(description);
		}
	}
	else if (target == "") {
		b = false;
	}
	return b;
}

/**
 * Populate action-list.
 *
 * @param el
 */
function zmiActionPopulate(el) {
	if ( el.options[el.options.length-1].text.indexOf('---') != 0) {
		return;
	}
	
	// Set wait-cursor.
	$(document.body).css( "cursor", "wait");
	
	// Get params.
	var action = self.location.href;
	action = action.substr(0,action.indexOf('?')>0?action.substr(0,action.indexOf('?')).lastIndexOf('/'):action.lastIndexOf('/'));
	var extrapath = '';
	var $anchor = $('a:first',$(el).parents('td')[0]);
	if ($anchor) {
		var anchorpath = $anchor.attr('href');
		if (typeof anchorpath != 'undefined') {
			var extrapath = anchorpath.split('/');
			if (extrapath.length > 2) {
				for ( var i = 0; i < extrapath.length - 2; i++) {
					action += '/'+extrapath[i];
				}
			}
		}
	}
	action += '/manage_ajaxZMIActions';
	var params = {};
	params['lang'] = getZMILang();
	params['context_id'] = $(el).attr('id').substr(zmiActionPrefix.length);
	// JQuery.AJAX.get
	$.get( action, params, function(data) {
		// Reset wait-cursor.
		$(document.body).css( "cursor", "auto");
		// Get object-id.
		var value = eval('('+data+')');
		var id = value['id'].replace(/\./,"_");
		var actions = value['actions'];
		var select = document.getElementById(zmiActionPrefix+id);
		if ( select.options[select.options.length-1].text.indexOf('---') != 0)
			return;
		for (var i = 1; i < actions.length; i++) {
			var optlabel = actions[i][0];
			var optvalue = '';
			if (extrapath.length > 2) {
				for ( var j = 0; j < extrapath.length - 2; j++) {
					optvalue += extrapath[j]+'/';
				}
			}
			optvalue += actions[i][1];
			var option = new Option( optlabel, optvalue);
			select.options[ select.length] = option;
		}
		select.selectedIndex = 0;
	});
}

/**
 * Execute action from select.
 *
 * @param fm
 * @param target
 * @param id
 * @param sort_id
 * @param custom
 */
function zmiActionExecute(fm, el, target, id, sort_id, custom) {
	var $fm = $(fm);
	$('input[id=id_prefix]',$fm).val( id);
	$('input[id=_sort_id]',$fm).val( sort_id);
	$('input[id=custom]',$fm).val( custom);
	if (target.toLowerCase().indexOf('manage_addproduct/')==0 && target.toLowerCase().indexOf('form')>0) {
		var html = '';
		html += '<tr id="tr_manage_addProduct" class="zmiTeaserColor">';
		html += '<td colspan="3"><div style="border:3px solid black"><img src="/misc_/zms/btn_add.gif" border="0" align="absmiddle"/> '+custom+'</div></td>';
		html += '</tr>';
		$(html).insertAfter($($(el).parents('tr')[0]));
		var inputs = $('input:hidden',$fm);
		var data = {};
		for ( var i = 0; i < inputs.length; i++) {
			var $input = $(inputs[i]);
			var id = $input.attr("id");
			if (jQuery.inArray(id,['form_id','id_prefix','_sort_id','custom','lang','preview'])>=0) {
				data[$input.attr('name')] = $input.val();
			}
		}
		// Show add-dialog.
		zmiIframe(target,data,{
				title:getZMILangStr('BTN_INSERT'),
				close:function(event,ui) {
					$('tr#tr_manage_addProduct').remove();
				}
		});
	}
	else {
		$fm.attr('action',target);
		$fm.unbind('submit');
		$fm.submit();
	}
}

/**
 * Choose action from select.
 *
 * @param e
 * @param id
 * @param sort_id
 */
function zmiActionChoose(e, id, sort_id) {
	var fm = $(e.form);
	var $input = $('input[name="ids:list"][value='+id+']:checkbox',fm);
	var i = e.selectedIndex;
	var label = e.options[i].text;
	var action = e.options[i].value;
	if (action.indexOf("%s/") == 0) {
		action = id + action.substring(2, action.length);
	}
	if (action.indexOf('?') > 0) {
		location.href = action;
	}
	else {
		// Set checkbox.
		$input.prop( "checked", true);
		// Confirm and execute.
		if (zmiConfirmAction(fm,action,label)) {
			zmiActionExecute(fm,e,action,id,sort_id,label);
		}
	}
	// Reset checkbox and select.
	$input.prop( "checked", false);
	e.selectedIndex = 0;
}


// ############################################################################
// ### Url-Input
// ############################################################################

/**
 * zmiBrowseObjs
 */
function zmiBrowseObjs(fmName, elName, lang) {
	var elValue = '';
	if (fmName.length>0 && elName.length>0) {
		elValue = $('form[name='+fmName+'] input[name='+elName+']').val();
	}
	var title = getZMILangStr('CAPTION_CHOOSEOBJ');
	var href = "manage_browse_iframe";
	href += '?lang='+lang;
	href += '&fmName='+fmName;
	href += '&elName='+elName;
	href += '&elValue='+escape(elValue);
	if ( selectedText) {
		href += '&selectedText=' + escape( selectedText);
	}
	if ($('#zmiDialog').length==0) {
		$('body').append('<div id="zmiDialog"></div>');
	}
	$('#zmiDialog').dialog({
			autoOpen: false,
			title: title,
			height: 'auto',
			width: 'auto'
		}).html('<iframe src="'+href+'" style="width:100%; min-width:'+getZMIConfProperty('zmiBrowseObjs.minWidth',200)+'px; height:100%; min-height: '+getZMIConfProperty('zmiBrowseObjs.minHeight',320)+'px; border:0;"></iframe>').dialog('open');
	return false;
}

function zmiBrowseObjsApplyUrlValue(fmName, elName, elValue) {
	$('form[name='+fmName+'] input[name='+elName+']').val(elValue).change();
}

function zmiDialogClose(id) {
	$('#'+id).dialog('close');
	$('body').remove('#'+id);
}