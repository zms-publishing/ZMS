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
	d['filename'] = $('#filename_'+elName).html();
	d['dimensions'] = $('#dimensions_'+elName).html();
	d['size'] = $('#size_'+elName).html();
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
			$el.removeClass("zmi-helper-hidden");
		}
		else {
			$el.show("normal");
		}
	}
	else {
		if (nodeName=="li") {
			$el.addClass("zmi-helper-hidden");
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
	$('#div_opaque_'+elName).remove();
}

/**
 * Click undo-button.
 */
function zmiUndoBlobBtnClick(elName) {
	// Undo delete.
	zmiUndoBlobDelete(elName);
	// Restore properties.
	var d = zmiBlobDict[elName];
	for (var k in d) {
		var v = d[k];
		$('#'+k+'_'+elName).html(v);
	}
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
		var l = ['filename','dimensions','size'];
		for (var i=0; i < l.length; i++) {
			$('#'+l[i]+'_'+elName).html('<del>'+$('#'+l[i]+'_'+elName).html()+'</del>');
		}
		// Create transparent overlay.
		var img = $('img#img_'+elName);
		if (img.length > 0) {
			$('body').append('<div id="div_opaque_'+elName+'" class="zmiDivOpaque">&nbsp;</div>');
			var div = $('div#div_opaque_'+elName);
			var pos = img.offset();
			div.css({
				position:'absolute',
				left:pos.left,
				top:pos.top,
				width:img.outerWidth(),
				height:img.outerHeight()
			});
		}
	}
	// Refresh buttons.
	zmiSwitchBlobButtons(elName);
}