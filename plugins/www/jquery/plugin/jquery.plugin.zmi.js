// ############################################################################
// ### Common
// ############################################################################

/**
 * Open link in iframe (jQuery UI Dialog).
 */
function zmiIframe(href, opt) {
	if ($('#zmiIframe').length==0) {
		$('body').append('<div id="zmiIframe"></div>');
	}
	$.get(href,function(result) {
			opt["modal"] = true;
			opt["height"] = "auto";
			opt["width"] = "auto";
			$('#zmiIframe').html(result);
			var title = $('#zmiIframe div.zmi').attr("title");
			if (typeof title != "undefined" && title) {
				opt["title"] = title;
			}
			$('#zmiIframe').dialog(opt);
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
		v = !$(':checkbox:not([name~=active])',fm).attr('checked');
	}
	$(':checkbox:not([name~=active])',fm).attr('checked',v)
}

// ############################################################################
// ### Forms
// ############################################################################

var zmiSortableRownum = null;

$(function(){
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
	// Action-Lists
	$("input.zmi-ids-list:checkbox").click( function(evt) { zmiActionButtonsRefresh(this,evt); } );
	$("select.zmi-action")
		.focus( function(evt) { zmiActionPopulate(this); })
		.mouseover( function(evt) { zmiActionPopulate(this); }
	);
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
});


// ############################################################################
// ### ZMI Action-Lists
// ############################################################################

var zmiActionPrefix = 'select_actions_';

/**
 * Populate action-list.
 *
 * @param el
 */
function zmiActionPopulate(el) 
{
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
		var href = target;
		var inputs = $('input:hidden',$fm);
		var q = '?';
		for ( var i = 0; i < inputs.length; i++) {
			href += q + $(inputs[i]).attr('name') + '=' + $(inputs[i]).val();
			q = '&amp;';
		}
		// Show add-dialog.
		zmiIframe(href,{
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
		}).html('<iframe src="'+href+'" style="width:100%; min-width:200px; height:100%; min-height: 320px; border:0;"></iframe>').dialog('open');
	return false;
}

function zmiBrowseObjsApplyUrlValue(fmName, elName, elValue) {
	$('form[name='+fmName+'] input[name='+elName+']').val(elValue);
}

function zmiDialogClose(id) {
	$('#'+id).dialog('close');
	$('body').remove('#'+id);
}

// ############################################################################
// ### Notification Service
// ############################################################################

/**
 *
 */
function zmiGetNotifications() {
	$.get('getNotifications',
		{},
		function(data) {
			if (data.length==0) {
				return;
			}
			var notifications = eval('('+data+')');
			var maxseverity = null;
			var html = '';
			for ( var i = 0; i < notifications.length; i++) {
				var notification = notifications[i];
				var severity = notification['severity'];
				html += '<div class="form-label">Current Messages:</div>';
				html += '<div class="form-small">';
				html += '<img src="/misc_/zms/ico_'+severity+'.gif" alt="" border="0" align="absmiddle"/> ';
				html += '<strong>'+notification['date']+'</strong> ';
				html += notification['html'];
				html += '</div>';
				if ((maxseverity == null)
					|| (severity == 'warning' && (maxseverity == 'info'))
					|| (severity == 'warning' && (maxseverity == 'info' || maxseverity == 'warning'))) {
					maxseverity = severity;
				}
			}
			if (maxseverity != null) {
				if ( $('#ZMIManageTabsButtons > li#ZMIManageTabsNotifications').length==0) {
					$('#ZMIManageTabsButtons').html('<li id="ZMIManageTabsNotifications"></li>'+$('#ZMIManageTabsButtons').html());
				}
				$('#ZMIManageTabsButtons > li#ZMIManageTabsNotifications').html(
					'<a href="#ZMIManageTabsNotificationsDiv"><img src="/misc_/zms/ico_'+maxseverity+'.gif" title="Click to open notifications..." border="0"></a>'+
					'<div style="display:none">'+
					'<div id="ZMIManageTabsNotificationsDiv">'+
					html+
					'</div>'+
					'</div>'+
					'');
				$('a[href=#ZMIManageTabsNotificationsDiv]').click(function(){
					showFancybox({href:$(this).attr('href')});
				});
			}
			setTimeout('zmiGetNotifications()',60000);
		});
}

/**
 *
 */
function zmiClearNotifications() {
}

/**
 *
 */
$(function() {
	zmiGetNotifications();
});

// ############################################################################
// ### Date Functions
// ############################################################################

/**
 * y2k
 */
function y2k(number) {
    rtn = number;
    if (rtn>=0 && rtn<50)
        rtn += 2000;
    else
    if (rtn>=50 && rtn<100)
        rtn += 1900;
    return (rtn < 1000) ? rtn + 1900 : rtn;
}

/**
 * isDate:
 *
 * checks if date passed is valid
 * will accept dates in following format:
 * isDate(dd,mm,ccyy), or
 * isDate(dd,mm) - which defaults to the current year, or
 * isDate(dd) - which defaults to the current month and year.
 * Note, if passed the month must be between 1 and 12, and the
 * year in ccyy format.
 */
function isDate (day,month,year) {
     var today = new Date();
     year = ((!year) ? y2k(today.getYear()):year);
     month = ((!month) ? today.getMonth():month-1);
     if (!day) return false
     var test = new Date(year,month,day);
     if ( (y2k(test.getYear())==year || y2k(test.getYear())==year+1900 || y2k(test.getYear())==year+2000) &&
          (month == test.getMonth()) &&
          (day == test.getDate()) )
     {
         return true;
     } else
     {
         return false;
     }
}

/**
 * parseDateInt:
 */
function parseDateInt(s) {
  while (s.length > 0 && s.indexOf("0") == 0)
    s = s.substring(1);
  if (s.length == 0)
    return 0;
  else
    return parseInt(s);
}

/**
 * validDate:
 */
function validDate(s) {
  return (getDate(s) != null)
}

/**
 * getDate:
 */
function getDate(s) {
  var now = new Date();
  var day = now.getDate();
  var month = now.getMonth()+1;
  var year = now.getYear();
  var daySep = s.indexOf(".",0);
  if (daySep >= 0) {
    var monthSep = s.indexOf( "." , daySep + 1 );
    if (monthSep >= 0) {
        day   = parseDateInt(s.substring( 0 , daySep ));
        month = parseDateInt(s.substring( daySep + 1 , monthSep ));
        year  = parseDateInt(s.substring( monthSep + 1 ));
    } else {
        day = parseDateInt(s.substring( 0 , daySep ));
        month = parseDateInt(s.substring( daySep + 1 ));
    }
  } else
     day = parseDateInt(s);

  if (isNaN(day) || isNaN(month) || isNaN(year))
      return null
  else {
      if (!isDate(day,month,year))
         return null;
      else {
         month = month-1;
         year = y2k(year);
         return new Date(year,month,day);
      }
  }
}

