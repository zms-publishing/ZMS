// /////////////////////////////////////////////////////////////////////////////
//  Auth
// /////////////////////////////////////////////////////////////////////////////

/**
 * Force change password.
 */
ZMI.prototype.forceChangePassword = function() {
	$("a#manage_userForm").click();
	$(".modal-header .close").hide();
}

// /////////////////////////////////////////////////////////////////////////////
//  Cookies
// /////////////////////////////////////////////////////////////////////////////

/**
 * Toggle cookie.
 */
ZMI.prototype.toggleCookie = function(key) {
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

// /////////////////////////////////////////////////////////////////////////////
//  Dimensions
// /////////////////////////////////////////////////////////////////////////////

/**
 * Returns coordinates of given element
 */
ZMI.prototype.getCoords = function(theElement, thePosition) {
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

// /////////////////////////////////////////////////////////////////////////////
//  Languages
// /////////////////////////////////////////////////////////////////////////////

/**
 * Get descendant languages.
 */
ZMI.prototype.getDescendantLanguages = function() {
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


// /////////////////////////////////////////////////////////////////////////////
//  RTE: Relative URLs.
// /////////////////////////////////////////////////////////////////////////////

/**
 * Relativate url.
 */
ZMI.prototype.relativateUrl = function(page_abs_url, url) {
	var protocol = self.location.href;
	protocol = protocol.substr(0,protocol.indexOf(":")+3);
	var server_url = self.location.href;
	server_url = server_url.substr(protocol.length);
	server_url = protocol + server_url.substr(0,server_url.indexOf("/"));
	var currntPath = null;
	if (page_abs_url.indexOf(server_url)==0) {
		currntPath = page_abs_url.substr(server_url.length+1);
	}
	else if (page_abs_url.indexOf('/')==0) {
		currntPath = page_abs_url.substr(1);
	}
	var targetPath = null;
	if (url.indexOf(server_url)==0) {
		targetPath = url.substr(server_url.length+1);
	}
	else if (url.indexOf('/')==0) {
		targetPath = url.substr(1);
	}
	if (currntPath == null || targetPath == null) {
		return url;
	}
	while ( currntPath.length > 0 && targetPath.length > 0) {
		var i = currntPath.indexOf( '/');
		var j = targetPath.indexOf( '/');
		if ( i < 0) {
			currntElmnt = currntPath;
		}
		else {
			currntElmnt = currntPath.substring( 0, i);
		}
		if ( j < 0) {
			targetElmnt = targetPath;
		}
		else {
			targetElmnt = targetPath.substring( 0, j);
		}
		if ( currntElmnt != targetElmnt) {
			break;
		}
		if ( i < 0) {
			currntPath = '';
		}
		else {
			currntPath = currntPath.substring( i + 1);
		}
		if ( j < 0) {
			targetPath = '';
		}
		else {
			targetPath = targetPath.substring( j + 1);
		}
	}
	while ( currntPath.length > 0) {
		var i = currntPath.indexOf( '/');
		if ( i < 0) {
			currntElmnt = currntPath;
			currntPath = '';
		}
		else {
			currntElmnt = currntPath.substring( 0, i);
			currntPath = currntPath.substring( i + 1);
		}
		targetPath = '../' + targetPath;
	}
	url = './' + targetPath;
	return url;
}

/**
 * Relativate urls.
 */
ZMI.prototype.relativateUrls = function(page_abs_url,html) {
	var splitTags = ['href="','src="'];
	for ( var h = 0; h < splitTags.length; h++) {
		var splitTag = splitTags[h];
		var vSplit = html.split(splitTag);
		var v = vSplit[0];
		for ( var i = 1; i < vSplit.length; i++) {
			var j = vSplit[i].indexOf('"');
			var url = vSplit[i].substring(0,j);
			if (url.indexOf('./')<0) {
				url = this.relativateUrl(page_abs_url,url);
			}
			v += splitTag + url + vSplit[i].substring(j);
		}
		html = v;
	}
	return html;
}