                                                                           /**
 * Returns language.
 */
function getZMILang() {
	if (typeof zmiParams['lang'] == 'undefined') {
		zmiParams['lang'] = zmiLangStr['lang'];
	}
	return zmiParams['lang'];
}

/**
 * Returns language-string.
 */
function getZMILangStr(key, data) {
	if (typeof data == "undefined") {
		data = {};
	}
	data['key'] = key; // @TODO
	if (typeof zmiLangStr[key] == 'undefined') {
		zmiLangStr[key] = key
	}
	return zmiLangStr[key];
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

/* +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
 * +- [ZMI] Dimensions
 * +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
 */

/**
 * Returns coordinates of given element
 */
function zmiGetCoords(theElement, thePosition) {
	var coords = {x: 0, y: 0};
	var element = theElement;
	while (element) {
		if (thePosition=="relative" && $(element).css("position")=="absolute") {
			break;
		}
		coords.x += element.offsetLeft;
		coords.y += element.offsetTop;
		element = element.offsetParent;
	}
	return coords;
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

