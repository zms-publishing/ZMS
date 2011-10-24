/**
 * Returns language.
 */
function getZMILang() {
	var lang = zmiParams['lang'];
	if (typeof lang != 'undefined') {
		return lang;
	}
	return $.ajax({
		url: 'getPrimaryLanguage',
		datatype:'text',
		async: false
		}).responseText;
}

/**
 * Returns language-string.
 */
function getZMILangStr(key, data) {
	if (typeof data == "undefined") {
		data = {};
	}
	data['key'] = key;
	return $.ajax({
		url: 'getZMILangStr',
		data: data,
		datatype: 'text',
		async: false
		}).responseText;
}

/**
 * Returns conf-property.
 */
function getZMIConfProperty(key, defaultValue) {
	var data  = {}
	data['key'] = key;
	if (typeof defaultValue != "undefined") {
		data['default'] = defaultValue;
	}
	return $.ajax({
		url: 'getConfProperty',
		data: data,
		datatype: 'text',
		async: false
		}).responseText;
}

/**
 * Confirm delete.
 *
 * @param href
 */
function confirmDeleteBtnOnClick(href) {
	if (confirm(getZMILangStr('MSG_CONFIRM_DELOBJ'))) {
		if (href.indexOf('lang=') < 0) {
			href += '&amp;lang='+getZMILang();
		}
		location.href = href;
	}
}

/**
 * Returns configuration-files.
 */
var zmiExpandConfFilesProgress = false;
function zmiExpandConfFiles(el, pattern) {
	if (!zmiExpandConfFilesProgress) {
		if ( el.options.length <=1) {
			zmiExpandConfFilesProgress = true;
			// Set wait-cursor.
			$(document.body).css( "cursor", "wait");
			// JQuery.AJAX.get
			$.get( 'getConfFiles',
				{id:el.id,pattern:pattern},
					function(data) {
						// Reset wait-cursor.
						$(document.body).css( "cursor", "auto");
						//
						var select = document.getElementById('init');
						var items = $("item",data);
						for (var i = 0; i < items.length; i++) {
							var item = $(items[i]);
							var value = item.attr("key");
							var label = item.text();
							var option = new Option( label, value);
							select.options[ select.length] = option;
						}
						select.selectedIndex = 0;
						zmiExpandConfFilesProgress = false;
					});
		}
	}
}

/**
 * collectionPositionPopulate
 *
 * @param el
 * @param len
 * @see f_collectionbtn.dtml
 */
function collectionPositionPopulate(el, len) {
	if ( el.options.length == 1) {
		selectedValue = el.options[0].text;
		el.options.length = 0;
		for (var i = 0; i < len; i++) {
			var value = ''+(i+1);
			addOption( el, value, value, selectedValue);
		}
	}
}

/**
 * collectionDeleteBtnOnClick
 *
 * @param href
 * @see f_collectionbtn.dtml
 */
function collectionDeleteBtnOnClick(href) {
	confirmDeleteBtnOnClick(href + '&amp;btn=delete');
}

/**
 * Toggle display of element.
 */
function toggleElement( selector) {
	var els = $(selector);
	if ( selector.indexOf("tr[")==0) {
		if (els.css("visibility")=='hidden') {
			els.css({'visibility':'visible','display':''});
		}
		else {
			els.css({'visibility':'hidden','display':'none'});
		}
	}
	else {
		if (els.css("display")=='none') {
			els.show('fast');
		}
		else {
			els.hide('fast');
		}
	}
	return;
}

/**
 * Toggle cookie.
 */
function toggleCookie( key) {
	runPluginCookies(function() {
		try {
			var value = $.cookies.get(key);
			if (value==null || value=='0') {
				$.cookies.set(key,'1');
			}
			else {
				$.cookies.del(key);
			}
		}
		catch(e) {
		}
	});
}

/**
 * Fire event.
 *
 * @see http://www.rakshith.net/blog/?p=35
 */
function fireEvent( el, evtName) {
  //On IE
  if( el.fireEvent)
  {
    el.fireEvent('on'+evtName);
  }
  //On Gecko based browsers
  if(document.createEvent)
  {
    var evt = document.createEvent('HTMLEvents');
    if(evt.initEvent)
    {
      evt.initEvent(evtName, true, true);
    }
    if ( el.dispatchEvent)
    {
      el.dispatchEvent(evt);
    }
  }
}

/* +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
 * +- [ZMI] Character Format
 * +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
 */

var selectedRange = null;
var selectedText = "";

/**
 */
function selectObject(path, title) {
  if (path.indexOf('{$')==0 && path.lastIndexOf('}')==path.length-1) {
    path = '<'+'dtml-var expr="getLinkUrl(\''+path+'\',REQUEST)"/>';
  }
  var fTag = 'a';
  var aTag = '<'+fTag+' href="'+path+'">';
  var eTag = '</'+fTag+'>';
  tagSelectedText( aTag, eTag, true);
}

/**
 * Remove tags from given string.
 */
function untag( s) {
  return s.replace( /<(..*?)>/g, '');
}

/**
 * Get tagged index of untagged string in given string.
 */
function taggedStart( s1, s2)
{
  var r = '';
  var b = true;
  for (var i = 0; i < s1.length; i++) {
    var c = s1.charAt( i);
    if ( b && c == '<')
      b = false;
    else if ( !b && c == '>')
      b = true;
    else if ( b)
      r += c;
    if ( r == s2)
      return i;
  }
  return -1;
}

function zmiWriteDebug(s) {
  if ($('textarea#debug').length==0) {
    $('body').append('<textarea id="debug" rows="50" cols="80"></textarea>');
  }
	$("textarea#debug").val("["+(new Date())+"] "+s+"\n"+$("textarea#debug").val());
}

/**
 * Tag selected text.
 */
function tagSelectedText( aTag, eTag, bMayHaveChanged) {
  var input = self.el;
  /* internet explorer */
  if( typeof document.selection != 'undefined') {
    if (bMayHaveChanged) {
      /* Selected range may have changed */
      while (selectedRange.text.indexOf(selectedText)!=0) {
        selectedRange.moveStart('character',1);
      }
      while (selectedRange.text!=selectedText) {
        selectedRange.moveEnd('character',-1);
      }
    }
    else {
      selectedRange = document.selection.createRange();
    }
    var selText = selectedRange.text;
    /* Strip trailing blanks */
    var trailingBlanks = '';
    while ( selText.length > 0 && selText.charAt( selText.length - 1) == ' ') {
      selText = selText.substr( 0, selText.length - 1);
      trailingBlanks += ' ';
    }
    if ( selText.length > 0) {
      /* Apply value */
      var newText;
      if ( aTag.length > 0 && typeof eTag == 'undefined') {
        newText = aTag + trailingBlanks;
      }
      else {
        newText = aTag + selText + eTag + trailingBlanks;
      }
      if (bMayHaveChanged && input.value.indexOf(selText)==0) {
        zmiWriteDebug("input.value='"+input.value+"'");
        zmiWriteDebug("selText='"+selText+"'");
        if (input.value==selText) {
          input.value = newText;
        }
        else if (input.value.substr(selText.length).indexOf(selText)<0) {
          input.value = input.value.replace(selText+trailingBlanks,newText);
        }
        else {
          alert("can't tag selected text");
        }
      }
      else {
        selectedRange.text = newText;
        /* Anpassen der Cursorposition */
        selectedRange = document.selection.createRange();
        selectedRange.moveStart('character', newText.length);
        selectedRange.select();
      }
    }
  }
  /* newer gecko-based browsers */
  else if( typeof input.selectionStart != 'undefined') {
    var start = self.selectionStart;
    var end = self.selectionEnd;
    var inpValue = input.value;
    var selText = inpValue.substring( start, end);
    // Strip trailing blanks
    var trailingBlanks = '';
    while ( selText.length > 0 && selText.charAt( selText.length - 1) == ' ') {
      selText = selText.substr( 0, selText.length - 1);
      trailingBlanks += ' ';
    }
    if ( selText.length > 0) {
      /* Apply value */
      var newText;
      if ( aTag.length > 0 && typeof eTag == 'undefined')
        newText = aTag + trailingBlanks;
      else
        newText = aTag + selText + eTag + trailingBlanks;
      input.value = input.value.substr( 0, start) + newText + input.value.substr( end);
      /* Anpassen der Cursorposition */
      var pos = start + newText.length;
      input.selectionStart = pos;
      input.selectionEnd = pos;
    }
  }
}

/**
 * Untag selected text.
 * Returns true if selected text was untagged, false otherwise.
 */
function untagSelectedText( fTag, fAttrs, ld, rd) {
  var input = self.el;
  /* internet explorer */
  if( typeof document.selection != 'undefined') {
    var selText = selectedRange.text;
    var startTag = ld+fTag;
    var endTag = ld+'/'+fTag+rd;
    if ( selText.indexOf(startTag) == 0 && selText.lastIndexOf(endTag) == selText.length - endTag.length) {
      selText = selText.substr( startTag.length + 1, selText.lastIndexOf( endTag) - startTag.length - 1); 
      /* Apply value */
      selectedRange.text = selText;
      return true;
    }
    else {
      selectedRange.moveStart('character', -(startTag.length+1));
      selectedRange.moveEnd('character', endTag.length);
      var taggedText = selectedRange.text;
      if ( taggedText.indexOf(startTag) == 0 && taggedText.lastIndexOf(endTag) == taggedText.length - endTag.length) {
        /* Apply value */
        selectedRange.text = selText;
        return true;
      }
      else if ( fAttrs.length > 0) {
        startTag += fAttrs;
        selectedRange.moveStart('character', -fAttrs.length);
        var taggedText = selectedRange.text;
        if ( taggedText.indexOf(startTag) == 0 && taggedText.lastIndexOf(endTag) == taggedText.length - endTag.length) {
          /* Apply value */
          selectedRange.text = selText;
          return true;
        }
      }
    }
  }
  /* newer gecko-based browsers */
  else if( typeof input.selectionStart != 'undefined') {
    var start = self.selectionStart;
    var end = self.selectionEnd;
    var inpValue = input.value;
    var selText = inpValue.substring( start, end);
    var tagStart = inpValue.substr( 0, start);
    var i = tagStart.length;
    var c = tagStart.charAt( i - 1);
    if ( c == '>') {
      /* Handle DTML in a.href */
      i--;
      var l = 1;
      while ( l > 0 && i > 0) {
        c = tagStart.charAt( i - 1);
        if ( c == rd)
          l++;
        if ( c == ld)
          l--;
        i--;
      }
      if ( i >= 0) {
        var tag = tagStart.substr( i);
        tagStart = tagStart.substr( 0, i);
        if ( tag.indexOf(ld+fTag) == 0 && tag.indexOf(rd) > 0) {
          var tagEnd = inpValue.substr( end);
          if ( tagEnd.indexOf(rd) > 0) {
            var tag = tagEnd.substr( 0, tagEnd.indexOf(rd) + 1);
            tagEnd = tagEnd.substr( tagEnd.indexOf(rd) + 1);
            if ( tag.indexOf(ld+'/'+fTag+rd) == 0) {
              input.value = tagStart + selText + tagEnd;
              return true;
            }
          }
        }
      }
    }
  }
  return false;
}

/**
 * Set text-format.
 */
function setTextFormat( fTag, ld, rd, lang) 
{
  var fAttrs = '';
  if (fTag.indexOf( ' ') > 0) {
    fAttrs = fTag.substring( fTag.indexOf( ' '));
    fTag = fTag.substring( 0, fTag.indexOf( ' '));
  }
  var input = self.el;
  selectedText = '';
  /* internet explorer */
  if( typeof document.selection != 'undefined') {
    selectedRange = document.selection.createRange();
    selectedText = selectedRange.text;
  }
  /* newer gecko-based browsers */
  else if( typeof input.selectionStart != 'undefined') {
    self.selectionStart = input.selectionStart;
    self.selectionEnd = input.selectionEnd;
    var start = self.selectionStart;
    var end = self.selectionEnd
    selectedText = input.value.substring( start, end);
  }
  if ( selectedText.length == 0)
    return;
  if ( !untagSelectedText( fTag, fAttrs, ld, rd)) {
    if (fTag == 'a' && selectedText.indexOf('http://') < 0 && selectedText.indexOf('@') < 0) {
      zmiBrowseObjs('','',lang);
    } 
    else {
      var aTag = ld
      aTag += fTag;
      if (fTag == 'a') {
        if (selectedText.indexOf("@")>0)
          aTag += ' href="mailto:' + selectedText + '"';
        else if (selectedText.indexOf("http://") < 0)
          aTag += ' href="http://' + selectedText + '" target="_blank"';
        else
          aTag += ' href="' + selectedText + '" target="_blank"';
      }
      else {
        aTag += fAttrs;
      }
      aTag += rd;
      var eTag = ld+'/'+fTag+rd;
      tagSelectedText( aTag, eTag);
    }
  }
}

/**
 * Insert tab into richedit-textarea.
 */
function zmiRicheditInsertTab( fmName, elName) 
{
    var doc = document;
    var fm = doc.forms[ fmName];
    var input = fm.elements[ elName];
    input.focus();
    var insText = '\t';
    /* internet explorer */
    if( typeof doc.selection != 'undefined') {
      selectedRange = doc.selection.createRange();
      // insert text
      selectedRange.text = insText;
    }
    /* newer gecko-based browsers */
    else if( typeof input.selectionStart != 'undefined') {
      // insert text
      var start = input.selectionStart;
      var end = input.selectionEnd;
      input.value = input.value.substr(0, start) + insText + input.value.substr(end);
      // cursor-position
      var pos = start + insText.length;
      input.selectionStart = pos;
      input.selectionEnd = pos;
    }
}

/**
 * Set text-format for input.
 */
function setTextFormatInput( fTag, fmName, elName, lang) 
{
  self.fm = document.forms[ fmName];
  self.el = self.fm.elements[ elName];
  if (typeof self.el == 'undefined') {
    self.el = document.getElementsByName(elName)[0];
  }
  setTextFormat( fTag, '<', '>', lang);
}

/**
 * Store caret.
 */
function storeCaret( textEl) 
{
  if (textEl.createTextRange)
    textEl.caretPos = document.selection.createRange().duplicate();
}


/* +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
 * +- [ZMI] Dimensions
 * +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
 */

/**
 * Returns coordinates of given element
 */
function getCoords(theElement) {
  var coords = {x: 0, y: 0};
  var element = theElement;
  while (element) {
    coords.x += element.offsetLeft;
    coords.y += element.offsetTop;
    element = element.offsetParent;
  }
  return coords;
}

/**
 * Returns body dimensions
 */
function getBodyDimensions() {
  if (document.body && document.body.offsetWidth) {
    var div = $('body>div');
    return {width: div.prop('offsetWidth'), height: div.prop('offsetHeight')};
  } else {
    return {width: 0, height: 0};
  }
}

/**
 * Returns inner dimensions
 */
function getInnerDimensions() {
  if (window.innerWidth) { // Mozilla/Firefox
    return {width: window.innerWidth, height: window.innerHeight};
  } else if (document.documentElement && document.documentElement.clientWidth) { // IE6/IE8
    return {width: document.documentElement.clientWidth, height: document.documentElement.clientHeight};
  } else if (document.body && document.body.clientWidth) {
    return {width: document.body.clientWidth, height: document.body.clientHeight};
  } else {
    return {width: 0, height: 0};
  }
}


/**
 * Opens url in new frame-window
 */
function open_frame(title,url,params,width,height,options) {
    href = "f_frame";
    href += "?" + params;
    href += "&p_url=" + url;
    href += "&p_title=" + title;
    if ( height > screen.availHeight || width > screen.availWidth) {
      if ( options.indexOf( "scrollbars=") < 0) {
        if ( height > screen.availHeight)
          height = screen.availHeight;
        if ( width > screen.availWidth)
          width = screen.availWidth;
        options += ",scrollbars=yes";
      }
    }
    var name = url;
    var i = name.lastIndexOf( "/");
    if ( i > 0) {
      name = name.substring(i+1);
    }
    else {
      name = url;
    }
    i = name.indexOf("?");
    if ( i > 0) {
      name = name.substring(0,i);
    }
    i = name.indexOf("-");
    if ( i > 0) {
      name = name.substring(0,i);
    }
    i = name.indexOf(".");
    if ( i > 0) {
      name = name.substring(0,i);
    }
    var msgWindow = open(href,name,"width=" + width + ",height=" + height
      + ",screenX=" + (screen.width-width)/2
      + ",screenY=" + (screen.height-height)/2
      + ",dependent=yes"
      + ",left=" + (screen.width-width)/2
      + ",top=" + (screen.height-height)/2
      + options
      );
    if ( msgWindow) {
      msgWindow.focus();
      if ( msgWindow.opener == null) {
        msgWindow.opener = self;
      }
    }
  }
