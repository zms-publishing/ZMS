// -----------------------------------------------------------------------------
// -- Action-selects 
// -----------------------------------------------------------------------------

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
	var i = countSelectedCheckboxes(fm,'ids');
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
	else if (target.indexOf("manage_executeMetacmd") >=0 ) {
		var description = $.ajax({
			url: 'getMetaCmdDescription',
			data:{name:label},
			datatype:'text',
			async: false
			}).responseText;
		if (description.length > 0) {
			b = confirm(description);
		}
	}
	else if (target == "") {
		b = false;
	}
	return b;
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
		$("input[name=ids:list][type=checkbox][value="+id+"]",fm).attr( 'checked', true);
		// Confirm and execute.
		if (zmiConfirmAction(fm,action,label)) {
			zmiActionExecute(fm,e,action,id,sort_id,label);
		}
	}
	// Reset checkbox and select.
	$("input[name=ids:list][type=checkbox][value="+id+"]",fm).attr( 'checked', false);
	e.selectedIndex = 0;
}

// -----------------------------------------------------------------------------
//  -- Action-Buttons
// -----------------------------------------------------------------------------

var zmiActionButtons = [
		{'id':'trash','standalone':false},
		{'id':'cut','standalone':false},
		{'id':'copy','standalone':false},
		{'id':'paste','standalone':true}
	];

/**
 *
 * @param sender
 * @param evt
 */
function zmiActionButtonsRefresh(sender,evt) {
	var fm = $(sender).parents('form');
	var ids = countSelectedCheckboxes(fm,'ids') > 0;
	// Switch buttons.
	for (var ac=0; ac<zmiActionButtons.length; ac++) {
		var id = zmiActionButtons[ac]['id'];
		var standalone = zmiActionButtons[ac]['standalone'];
		var active = ids || standalone;
		var $li = $("span[id^="+id+"Btn]").parents("li");
		if (active) {
			$li.addClass("ui-state-default");
		}
		else {
			$li.removeClass("ui-state-default");
		}
	}
	// Switch selected rows.
	var clazz = "zmiTeaserColor";
	var els = $("input[name=ids:list][type=checkbox]");
	for (var i = 0; i < els.length; i++) {
		var tr = $($(els[i]).parents("tr")[0]);
		if (els[i].checked) {
			tr.addClass( clazz);
		}
		else {
			tr.removeClass( clazz);
		}
	}
	// Consume event!
	if (evt) {
		evt.stopPropagation();
	}
}

/**
 *
 * @param sender
 * @param ac		Action-Code
 * @param target
 * @param sort_id
 */
function zmiActionButtonClick(sender, ac, target, sort_id) {
	var fm = $(sender).parents('form');
	// Switch button.
	var ids = countSelectedCheckboxes(fm,'ids') > 0;
	var standalone = zmiActionButtons[ac]['standalone'];
	if (ids || standalone) {
		// Confirm and execute.
		if (zmiConfirmAction(fm,target)) {
			zmiActionExecute(fm, sender, target,'e',sort_id);
		}
	}
}

/**
 * This method (un-)checks all id-checkboxes on page and refreshs the buttons.
 *
 * @param sender
 * @param v		Boolean value for new (un-)checked state.
 */
function zmiToggleSelectionButtonClick(sender) 
{
	var fm = $(sender).parents('form');
	selectCheckboxes(fm,!$('input[type=checkbox]',fm).attr('checked'));
	zmiActionButtonsRefresh();
}