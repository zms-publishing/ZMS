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
			$li.show("normal");
		}
		else {
			$li.hide("normal");
		}
	}
	// Switch selected rows.
	var clazz = "zmiTeaserColor";
	var els = $("input[name=\x22ids:list\x22]:checkbox");
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
	zmiActionButtonsRefresh(sender);
}