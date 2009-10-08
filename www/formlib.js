 //-------------------------------------------------------------------
 // isNull(value)
 //   Returns true if value is null
 //-------------------------------------------------------------------
 function isNull(val) {
         if (val == null) { return true; }
         return false;
         }

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
 // isInteger(value)
 //   Returns true if value contains all digits
 //-------------------------------------------------------------------
 function isInteger(val) {
         for (var i=0; i < val.length; i++) {
                 if (!isDigit(val.charAt(i))) { return false; }
                 }
         return true;
         }

 //-------------------------------------------------------------------
 // isNumeric(value)
 //   Returns true if value contains a positive float value
 //-------------------------------------------------------------------
 function isNumeric(val) {
         var dp = false;
         for (var i=0; i < val.length; i++) {
                 if (!isDigit(val.charAt(i))) {
                         if (val.charAt(i) == '.') {
                                 if (dp == true) { return false; } // already saw a decimal point
                                 else { dp = true; }
                                 }
                         else {
                                 return false;
                                 }
                         }
                 }
         return true;
         }

 //-------------------------------------------------------------------
 // isDigit(value)
 //   Returns true if value is a 1-character digit
 //-------------------------------------------------------------------
 function isDigit(num) {
         var string="1234567890";
         if (string.indexOf(num) != -1) {
                 return true;
                 }
         return false;
         }

 //-------------------------------------------------------------------
 // setNullIfBlank(input_object)
 //   Sets a form field to "" if it isBlank()
 //-------------------------------------------------------------------
 function setNullIfBlank(obj) {
         if (isBlank(obj.value)) {
                 obj.value = "";
                 }
         }

 //-------------------------------------------------------------------
 // setFieldsToUpperCase(input_object)
 //   Sets value of form field toUpperCase() for all fields passed
 //-------------------------------------------------------------------
 function setFieldsToUpperCase() {
         for (var i=0; i<arguments.length; i++) {
           var obj = arguments[i];
           obj.value = obj.value.toUpperCase();
         }
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
 // disallowModify(input_object[,message[,true]])
 //   Checks a form field for a value different than defaultValue.
 //   Optionally alerts and focuses
 //-------------------------------------------------------------------
 function disallowModify(obj) {
         var msg;
         var dofocus;
         if (arguments.length>1) { msg = arguments[1]; }
         if (arguments.length>2) { dofocus = arguments[2]; } else { dofocus=false; }
         if (getInputValue(obj) != getInputDefaultValue(obj)) {
                 if (!isBlank(msg)) {
                         alert(msg);
                         }
                 if (dofocus) {
                         obj.select();
                         obj.focus();
                         }
                 setInputValue(obj,getInputDefaultValue(obj));
                 return true;
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
 // floatInputChange(input_object)
 //-------------------------------------------------------------------
 function floatInputChange(input_object) {
   var ok = !isNaN(input_object.value);
   if (!ok) {
     alert(">"  + input_object.value + "< is not a valid 'float'-value!");
     input_object.value = s;
     input_object.focus();
     return false;
   }
   return true;
 }

 //-------------------------------------------------------------------
 // floatInputChange(input_object)
 //-------------------------------------------------------------------
 function intInputChange(input_object) {
   var ok = true;
   var s = "";
   for (i=0; i<input_object.value.length; i++) {
       ch = input_object.value.charAt(i);
       ch_ok =
          (ch == '0' || ch == '1' || ch == '2' || ch == '3' || ch == '4' ||
       	  ch == '5' || ch == '6' || ch == '7' || ch == '8' || ch == '9');
       ok = ok && ch_ok;
       if (ch_ok)
         s += ch;
   }
   if (!ok) {
     alert(">"  + input_object.value + "< is not a valid 'int'-value!");
     input_object.value = s;
     input_object.focus();
     return false;
   }
   return true;
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
 // getInputValue(input_object)
 //   Get the value of any form input field
 //   Multiple-select fields are returned as comma-separated values
 //   (Doesn't support input types: button,file,password,reset,submit)
 //-------------------------------------------------------------------
 function getInputValue(obj) {
         if ((typeof obj.type != "string") && (obj.length > 0) && (obj[0] != null) && (obj[0].type=="radio")) {
                 for (var i=0; i<obj.length; i++) {
                         if (obj[i].checked == true) { return obj[i].value; }
                         }
                 return "";
                 }
         if (obj.type=="text")
                 { return obj.value; }
         if (obj.type=="hidden")
                 { return obj.value; }
         if (obj.type=="textarea")
                 { return obj.value; }
         if (obj.type=="checkbox") {
                 if (obj.checked == true) {
                         return obj.value;
                         }
                 return "";
                 }
         if (obj.type=="select-one") {
                 if (obj.options.length > 0) {
                         return obj.options[obj.selectedIndex].value;
                         }
                 else {
                         return "";
                         }
                 }
         if (obj.type=="select-multiple") {
                 var val = "";
                 for (var i=0; i<obj.options.length; i++) {
                         if (obj.options[i].selected) {
                                 val = val + "" + obj.options[i].value + ",";
                                 }
                         }
                 if (val.length > 0) {
                         val = val.substring(0,val.length-1); // remove trailing comma
                         }
                 return val;
                 }
         return "";
         }

 //-------------------------------------------------------------------
 // getInputDefaultValue(input_object)
 //   Get the default value of any form input field when it was created
 //   Multiple-select fields are returned as comma-separated values
 //   (Doesn't support input types: button,file,password,reset,submit)
 //-------------------------------------------------------------------
 function getInputDefaultValue(obj) {
         if ((typeof obj.type != "string") && (obj.length > 0) && (obj[0] != null) && (obj[0].type=="radio")) {
                 for (var i=0; i<obj.length; i++) {
                         if (obj[i].defaultChecked == true) { return obj[i].value; }
                         }
                 return "";
                 }
         if (obj.type=="text")
                 { return obj.defaultValue; }
         if (obj.type=="hidden")
                 { return obj.defaultValue; }
         if (obj.type=="textarea")
                 { return obj.defaultValue; }
         if (obj.type=="checkbox") {
                 if (obj.defaultChecked == true) {
                         return obj.value;
                         }
                 return "";
                 }
         if (obj.type=="select-one") {
                 if (obj.options.length > 0) {
                         for (var i=0; i<obj.options.length; i++) {
                                 if (obj.options[i].defaultSelected) {
                                         return obj.options[i].value;
                                         }
                                 }
                         }
                 return "";
                 }
         if (obj.type=="select-multiple") {
                 var val = "";
                 for (var i=0; i<obj.options.length; i++) {
                         if (obj.options[i].defaultSelected) {
                                 val = val + "" + obj.options[i].value + ",";
                                 }
                         }
                 if (val.length > 0) {
                         val = val.substring(0,val.length-1); // remove trailing comma
                         }
                 return val;
                 }
         return "";
         }

 //-------------------------------------------------------------------
 // setInputValue()
 //   Set the value of any form field. In cases where no matching value
 //   is available (select, radio, etc) then no option will be selected
 //   (Doesn't support input types: button,file,password,reset,submit)
 //-------------------------------------------------------------------
 function setInputValue(obj,val) {
         if ((typeof obj.type != "string") && (obj.length > 0) && (obj[0] != null) && (obj[0].type=="radio")) {
                 for (var i=0; i<obj.length; i++) {
                         if (obj[i].value == val) {
                                 obj[i].checked = true;
                                 }
                         else {
                                 obj[i].checked = false;
                                 }
                         }
                 }
         if (obj.type=="text")
                 { obj.value = val; }
         if (obj.type=="hidden")
                 { obj.value = val; }
         if (obj.type=="textarea")
                 { obj.value = val; }
         if (obj.type=="checkbox") {
                 if (obj.value == val) { obj.checked = true; }
                 else { obj.checked = false; }
                 }
         if ((obj.type=="select-one") || (obj.type=="select-multiple")) {
                 for (var i=0; i<obj.options.length; i++) {
                         if (obj.options[i].value == val) {
                                 obj.options[i].selected = true;
                                 }
                         else {
                                 obj.options[i].selected = false;
                                 }
                         }
                 }
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
                         var type = theform[name].type;
                         if (!ignoreFields[name]) {
                                 if (type=="hidden" && hiddenFields[name]) {
                                         changed = isChanged(theform[name]);
                                         }
                                 else if (type=="hidden") {
                                         changed = false;
                                         }
                                 else {
                                         changed = isChanged(theform[name]);
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
// selectCheckboxes(fm, v)
//  Un-/select checkboxes.
//-------------------------------------------------------------------
function selectCheckboxes(fm, v)
	{
	  $(':checkbox:not([name~=active])',fm).attr('checked',v)
	}

//-------------------------------------------------------------------
// countSelectedCheckboxes(fm)
//  Count selected checkboxes.
//-------------------------------------------------------------------
function countSelectedCheckboxes(fm, elNamePrefix) {
	    var counter = 0;
	    for (var i=0;i<fm.elements.length;i++) {
	      var e = fm.elements[i];
	      if (e.type == 'checkbox' && e.checked)
	        if (elNamePrefix) {
	          if (e.name.indexOf(elNamePrefix)==0)
	            counter++;
	        }
	        else {
	          counter++;
	        }
	    }
	    return counter;
  }

//-------------------------------------------------------------------
// getSelectedCheckboxes(fm)
//  Get selected checkboxes als url-param.
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
      $('option',ms).attr("selected","selected");
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
function appendToMultiselect(src,data) {
		for ( var i = 0; i < src.options.length; i++) {
			if ( src.options[i].value == data) {
				return;
			}
		}
		var label = data;
		var value = data;
		var defaultSelected = false;
		var option = new Option( label, value, defaultSelected);
		src.options[ src.length] = option;
	}

//-------------------------------------------------------------------
// selectFromMultiselect
//-------------------------------------------------------------------
function selectFromMultiselect(fmName, srcElName, dstElName) {
    var fm = document.forms[fmName];
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
function selectAllFromMultiselect(fmName, srcElName, dstElName) {
    var fm = document.forms[fmName];
    var src = fm.elements[srcElName];
    var dst = fm.elements[dstElName];
    var index = 0;
    while (index < src.options.length) {
      src.options[index].selected = true;
      index++;
    }
    selectFromMultiselect(fmName,srcElName,dstElName);
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
