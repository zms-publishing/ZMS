// /////////////////////////////////////////////////////////////////////////////
//  Config
// /////////////////////////////////////////////////////////////////////////////

/**
 * Returns configuration-files.
 */
var zmiExpandConfFilesProgress = false;
function zmiExpandConfFiles(el, pattern) {
	if (!zmiExpandConfFilesProgress) {
		if ( $("option",el).length==1) {
			zmiExpandConfFilesProgress = true;
			// Set wait-cursor.
			$ZMI.setCursorWait("zmiExpandConfFiles");
			var first = null;
			if ( $("option",el).length==1) {
				first = $("option:first",el).html();
				$("option:first",el).html(getZMILangStr('MSG_LOADING'));
			}
			// JQuery.AJAX.get
			$.get( 'getConfFiles',{pattern:pattern},function(data) {
						if (first!=null) {
							$("option:first",el).html(first);
						}
						var items = $("item",data);
						for (var i = 0; i < items.length; i++) {
							var item = $(items[i]);
							var value = item.attr("key");
							var label = item.text();
							$(el).append('<option value="'+value+'">'+label+'</option>');
						}
						zmiExpandConfFilesProgress = false;
						// Reset wait-cursor.
						$ZMI.setCursorAuto("zmiExpandConfFiles");
					});
		}
	}
}

 / /////////////////////////////////////////////////////////////////////////////
//  Multiselect
// /////////////////////////////////////////////////////////////////////////////

/**
 * Process multiselects on form-submit:
 * select options
 */
function processMultiselectsOnFormSubmit() {
	// lazy multiselects (all elements starting with 'src')
	var mss = $('select[multiple]');
	for (var i=0; i < mss.length; i++) {
		var ms = $(mss[i]);
		if (ms.attr('name').indexOf('zms_mms_src_')!=0) {
			$('option',ms).prop("selected",true);
		}
	}
}

/**
 * Remove option from multiselect
 */
ZMI.prototype.removeFromMultiselect = function(src) { 
	if (typeof src == "string") {
		src = document.getElementById(src);
	}
	var selected = new Array(); 
	var index = 0; 
	while (index < src.options.length) { 
		if (src.options[index].selected) { 
			selected[index] = src.options[index].selected; 
		} 
		index++; 
	}
	index = 0; 
	var count = 0; 
	while (index < selected.length) { 
		if (selected[index]) 
			src.options[count] = null; 
		else 
			count++; 
		index++; 
	} 
	sortOptions(src); 
}

/**
 * Append option to multiselect
 */
ZMI.prototype.appendToMultiselect = function(src, data, defaultSelected) {
	var label = data;
	var value = data;
	if (typeof data == "object") {
		label = data.label;
		value = data.value;
		if (data.orig) {
			label = data.orig;
		}
	}
	if (typeof src == "string") {
		src = document.getElementById(src);
	}
	for ( var i = 0; i < src.options.length; i++) {
		if ( src.options[i].value == value) {
			return;
		}
	}
	if (typeof defaultSelected == "undefined") {
		defaultSelected = false;
	}
	var option = new Option( label, value, defaultSelected);
	src.options[ src.length] = option;
}

/**
 * Select single option from multiselect.
 */
ZMI.prototype.selectFromMultiselect = function(fm, srcElName, dstElName) {
	var src = fm.elements[srcElName];
	var dst = fm.elements[dstElName];
	var selected = new Array();
	var index = 0;
	while (index < src.options.length) {
		if (src.options[index].selected) {
			var newoption = new Option(src.options[index].text, src.options[index].value, true, true);
			dst.options[dst.length] = newoption;
			selected[index] = src.options[index].selected;
		}
		index++;
	}
	index = 0;
	var count = 0;
	while (index < selected.length) {
		if (selected[index])
			src.options[count] = null;
		else
			count++;
		index++;
	}
	sortOptions(src);
	sortOptions(dst);
	return false;
}

/**
 * Select all options from multiselect.
 */
ZMI.prototype.selectAllFromMultiselect = function(fm, srcElName, dstElName) {
	var src = fm.elements[srcElName];
	var dst = fm.elements[dstElName];
	var index = 0;
	while (index < src.options.length) {
		src.options[index].selected = true;
		index++;
	}
	this.selectFromMultiselect(fm,srcElName,dstElName);
	return false;
}

/**
 * Add option.
 *
 * @param object
 * @param name
 * @param value
 * @param selectedValue
 */
function addOption( object, name, value, selectedValue) {
	var defaultSelected = value.length > 0 && value == selectedValue;
	var selected = value.length > 0 && value == selectedValue;
	object.options[object.length] = new Option( name, value, defaultSelected, selected);
}
  
/**
 * Sort options.
 */
function sortOptions(what) {
	var copyOption = new Array();
	for (var i=0;i<what.options.length;i++)
		copyOption[i] = new Array(what[i].text,what[i].value);
	copyOption.sort();
	for (var i=what.options.length-1;i>-1;i--) {
		what.options[i] = null;
	}
	for (var i=0;i<copyOption.length;i++)
		addOption(what,copyOption[i][0],copyOption[i][1])
}
