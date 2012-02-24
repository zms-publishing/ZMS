 //-------------------------------------------------------------------
 // isBlank(value)
 //   Returns true if value only contains spaces
 //-------------------------------------------------------------------
 function isBlank(val) {
         if (val == null) { return true; }
         for (var i=0; i < val.length; i++) {
                 if ((val.charAt(i) != ' ') && (val.charAt(i) != "\t") && (val.charAt(i) != "\n")) { return false; }
                 }
         return true;
         }

 //-------------------------------------------------------------------
 // disallowBlank(input_object[,message[,true]])
 //   Checks a form field for a blank value. Optionally alerts if
 //   blank and focuses
 //-------------------------------------------------------------------
 function disallowBlank(obj) {
         var msg;
         var dofocus;
         if (arguments.length>1) { msg = arguments[1]; }
         if (arguments.length>2) { dofocus = arguments[2]; } else { dofocus=false; }
         if ( obj) {
         if ( obj.type) {
           if (isBlank(obj.value)) {
             if (!isBlank(msg)) {
               alert(msg);
             }
             if (dofocus) {
               if (!(obj.type == 'select-one' || obj.type == 'select-multiple')) {
                 obj.select();
               }
               obj.focus();
             }
             return true;
           }
         }
         else if ( obj.length) {
           var blank = true;
           for (var i=0; i<obj.length; i++) {
             if ( obj[i].type == 'radio' || obj[i].type == 'checkbox') {
               blank &= !obj[i].checked || isBlank(obj[i].value);
             }
           }
           if ( blank) {
             if (!isBlank(msg)) {
               alert(msg);
             }
             return true;
           }
         }
         }
         return false;
 }

 //-------------------------------------------------------------------
 // inputValue(v)
 //-------------------------------------------------------------------
function inputValue(v) {
  while (true) {
    var i = v.indexOf(unescape("%0A"));
    if (i<0) break;
    v = v.substring(0,i)+v.substring(i+1)
  }
  while (true) {
    var i = v.indexOf(unescape("%0D"));
    if (i<0) break;
    v = v.substring(0,i)+v.substring(i+1)
  }
  return v;
}

 //-------------------------------------------------------------------
 // isChanged(input_object)
 //   Returns true if input object's state has changed since it was
 //   created.
 //-------------------------------------------------------------------
 function isChanged(obj) {
         if ((typeof obj.type != "string") && (obj.length > 0) && (obj[0] != null) && (obj[0].type=="radio")) {
           for (var i=0; i<obj.length; i++) {
             if (obj[i].checked != obj[i].defaultChecked) {
               return true;
             }
           }
           return false;
         }
         if ((obj.type=="text") || (obj.type=="hidden") || (obj.type=="textarea")) {
           var v = inputValue(obj.value);
           var dv = inputValue(obj.defaultValue);
           changed = (v != dv);
           return changed;
         }
         if (obj.type=="checkbox") {
           return (obj.checked != obj.defaultChecked);
         }
         if (obj.type=="select-one") {
                 if (obj.options.length > 0) {
                         var x=0;
                         for (var i=0; i<obj.options.length; i++) {
                           if (obj.options[i].defaultSelected) { x++; }
                         }
                         if (x==0 && obj.selectedIndex==0) {
                           return false;
                         }
                         for (var i=0; i<obj.options.length; i++) {
                           if (obj.options[i].selected != obj.options[i].defaultSelected) {
                             return true;
                           }
                         }
                 }
                 return false;
                 }
         if (obj.type=="select-multiple") {
                 if (obj.options.length > 0) {
                         for (var i=0; i<obj.options.length; i++) {
                                 if (obj.options[i].selected != obj.options[i].defaultSelected) {
                                         return true;
                                         }
                                 }
                         }
                 return false;
                 }
         // return false for all other input types (button, image, etc)
         return false;
         }

 //-------------------------------------------------------------------
 // isFormModified(form_object,hidden_fields,ignore_fields)
 //   Check to see if anything in a form has been changed. By default
 //   it will check all visible form elements and ignore all hidden
 //   fields.
 //   You can pass a comma-separated list of field names to check in
 //   addition to visible fields (for hiddens, etc).
 //   You can also pass a comma-separated list of field names to be
 //   ignored in the check.
 //-------------------------------------------------------------------
 function isFormModified(theform, hidden_fields, ignore_fields) {
         if (hidden_fields == null) { hidden_fields = ""; }
         if (ignore_fields == null) { ignore_fields = ""; }

         var hiddenFields = new Object();
         var ignoreFields = new Object();
         var i,field;

         var hidden_fields_array = hidden_fields.split(',');
         for (i=0; i<hidden_fields_array.length; i++) {
                 hiddenFields[hidden_fields_array[i].basicTrim()] = true;
                 }
         var ignore_fields_array = ignore_fields.split(',');
         for (i=0; i<ignore_fields_array.length; i++) {
                 ignoreFields[ignore_fields_array[i].basicTrim()] = true;
                 }
         for (i=0; i<theform.elements.length; i++) {
                 var changed = false;
                 var name = theform.elements[i].name;
                 if (!isBlank(name)) {
                         var type = theform.elements[i].type;
                         if (!ignoreFields[name]) {
                                 if (type=="hidden" && hiddenFields[name]) {
                                         changed = isChanged(theform.elements[i]);
                                         }
                                 else if (type=="hidden") {
                                         changed = false;
                                         }
                                 else {
                                         changed = isChanged(theform.elements[i]);
                                         }
                                 }
                         }
                 if (changed) {
                         return true;
                         }
                 }
                 return false;
         }

//-------------------------------------------------------------------
// countSelectedCheckboxes(fm)
//  Count selected checkboxes.
//-------------------------------------------------------------------
function countSelectedCheckboxes(fm, elNamePrefix) {
    return $("input[name^="+elNamePrefix+"]:checked").length;
  }

//-------------------------------------------------------------------
// getSelectedCheckboxes(fm)
//  Get selected checkboxes as url-param.
//-------------------------------------------------------------------
function getSelectedCheckboxes(fm, elNamePrefix, newElNamePrefix) {
	    var param = '';
	    for (var i=0;i<fm.elements.length;i++) {
	      var e = fm.elements[i];
	      if (e.type == 'checkbox' && e.checked)
	        if (elNamePrefix) {
	          if (e.name.indexOf(elNamePrefix)==0)
	            if (param.length>0)
	              param += '&';
	            if (newElNamePrefix)
	              param += newElNamePrefix + e.name.substr(elNamePrefix.length) + '=' + escape(e.value);
	            else
	              param += e.name + '=' + escape(e.value);
	        }
	        else {
	          if (param.length>0)
	            param += '&';
	          param += e.name + '=' + escape(e.value);
	        }
	    }
	    return param;
  }
//-------------------------------------------------------------------
// processMultiselectsOnFormSubmit
//-------------------------------------------------------------------
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

//-------------------------------------------------------------------
// removeFromMultiselect
//-------------------------------------------------------------------
function removeFromMultiselect(src) {
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

//-------------------------------------------------------------------
// appendToMultiselect
//-------------------------------------------------------------------
function appendToMultiselect(src, data, defaultSelected) {
		for ( var i = 0; i < src.options.length; i++) {
			if ( src.options[i].value == data) {
				return;
			}
		}
		var label = data;
		var value = data;
		if (typeof data == "object") {
			label = data.label;
			value = data.value;
			if (data.orig) {
				label = data.orig;
			}
		}
		if (typeof defaultSelected == "undefined") {
			defaultSelected = false;
		}
		var option = new Option( label, value, defaultSelected);
		src.options[ src.length] = option;
	}

//-------------------------------------------------------------------
// selectFromMultiselect
//-------------------------------------------------------------------
function selectFromMultiselect(fm, srcElName, dstElName) {
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

//-------------------------------------------------------------------
// selectAllFromMultiselect
//-------------------------------------------------------------------
function selectAllFromMultiselect(fm, srcElName, dstElName) {
    var src = fm.elements[srcElName];
    var dst = fm.elements[dstElName];
    var index = 0;
    while (index < src.options.length) {
      src.options[index].selected = true;
      index++;
    }
    selectFromMultiselect(fm,srcElName,dstElName);
    return false;
  }

/**
 * Delete option.
 *
 * @param el
 */
function deleteOption(object,index) {
    object.options[index] = null;
}

/**
 * Add option.
 *
 * @param el
 * @param name
 * @param value
 * @param selectedValue
 */
function addOption( object, name, value, selectedValue) 
{
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
    for (var i=what.options.length-1;i>-1;i--)
      deleteOption(what,i);
    for (var i=0;i<copyOption.length;i++)
      addOption(what,copyOption[i][0],copyOption[i][1])
}
