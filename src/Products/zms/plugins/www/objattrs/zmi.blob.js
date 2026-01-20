/**
 * Functions for common blob-editing.
 */

var zmiBlobDict = {}
var zmiBlobParamsDict = {}

/**
 * Register blob.
 */
function zmiRegisterBlob(elName) {
	// Backup contents for undo
	var d = {}
	d['filename'] = $('#filename_'+elName).attr('data-filename');
	d['dimensions'] = $('#filename_'+elName).attr('data-dimensions');
	d['size'] = $('#filename_'+elName).attr('data-size');
	d['ZMSGraphic_extEdit_preview'] = $('#ZMSGraphic_extEdit_preview_'+elName).html();
	zmiBlobDict[elName] = d;
	// Initialize
	zmiBlobParamsDict[elName] = null;
}

/**
 * Register params for temp_folder.
 */
function zmiRegisterParams(elName, params) {
	zmiBlobParamsDict[elName] = params;
}

/**
 * Toggle blob-button (undo & delete).
 */
function zmiToggleBlobButton(elName, b) {
	var $el = $(elName);
	if (b) {
		var nodeName = typeof $el.prop("nodeName")=="undefined"?"":$el.prop("nodeName").toLowerCase();
		if (nodeName=="li") {
			$el.removeClass("d-none");
		}
		else {
			$el.show("normal");
		}
	}
	else {
		if (nodeName=="li") {
			$el.addClass("d-none");
		}
		else {
			$el.hide("normal");
		}
	}
}

/**
 * Switch blob-buttons (undo & delete).
 */
function zmiSwitchBlobButtons(elName) {
	var canUndo = false;
	var d = zmiBlobDict[elName];
	for (var k in d) {
		var v = d[k];
		canUndo |= $('#'+k+'_'+elName).html() != v;
	}
	zmiToggleBlobButton("#undo_btn_"+elName,canUndo);
	var canDelete = $('input[name=del_'+elName+']').val()!=1;
	zmiToggleBlobButton("#delete_btn_"+elName,canDelete);
}

/**
 * Undo delete.
 */
function zmiUndoBlobDelete(elName) {
	// Reset flag.
	$('input[name=del_'+elName+']').val(0);
	// Remove transparent overlay.
	var img = $('img#img_'+elName);
	if (img.length > 0) {
		img.removeClass('deleted');
	}
}

/**
 * Click undo-button.
 */
function zmiUndoBlobBtnClick(elName) {
	// Undo delete.
	zmiUndoBlobDelete(elName);
	// Restore properties.
	$('#filename_'+elName+' label del').contents().unwrap();
	// Remove from temp_folder.
	var params = zmiBlobParamsDict[elName];
	if ( params != null) {
		$.get('clearTempBlobjProperty',params);
	}
	zmiBlobParamsDict[elName] = null;
	// Refresh buttons.
	zmiSwitchBlobButtons(elName);
}

/**
 * Click delete-button.
 */
function zmiDelBlobBtnClick(elName) {
	if ($('input[name=del_'+elName+']').val()!=1) {
		// Apply flag.
		$('input[name=del_'+elName+']').val(1);
		// Clear properties.
		$('#filename_'+elName+' label').contents().wrap('<del>');
		// Create transparent overlay.
		var img = $('img#img_'+elName);
		if (img.length > 0) {
			img.addClass('deleted');
		}
	}
	// Refresh buttons.
	zmiSwitchBlobButtons(elName);
}

$(function() {
	$(".zmi-image,.zmi-file").each(function() {
			$(this).addClass("d-flex align-items-center");
			var elName = $(this).attr("id");
			elName = elName.substring(elName.lastIndexOf("-")+1);
			zmiRegisterBlob(elName);
			$("#delete_btn_"+elName,this).attr("href","javascript:zmiDelBlobBtnClick('"+elName+"')");
			$("#undo_btn_"+elName,this).attr("href","javascript:zmiUndoBlobBtnClick('"+elName+"')");
			zmiSwitchBlobButtons(elName);
		});
	});