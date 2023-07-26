String.prototype.removeWhiteSpaces = function() {return(this.replace(/\s+/g,""));};
String.prototype.leftTrim = function() {return(this.replace(/^\s+/,""));};
String.prototype.rightTrim = function() {return(this.replace(/\s+$/,""));};
String.prototype.basicTrim = function() {return(this.replace(/\s+$/,"").replace(/^\s+/,""));};
String.prototype.superTrim = function() {return(this.replace(/\s+/g," ").replace(/\s+$/,"").replace(/^\s+/,""));};
String.prototype.startsWith = function(str) {return (this.match("^"+str)==str)};
String.prototype.endsWith = function(str) {return (this.match(str+"$")==str)};
Array.prototype.indexOf = function(obj) {var i,idx=-1;for(i=0;i<this.length;i++){if(this[i]==obj){idx=i;break;}}return idx;};
Array.prototype.lastIndexOf = function(obj) {this.reverse();var i,idx=-1;for(i=0;i<this.length;i++){if(this[i]==obj){idx=(this.length-1-i);break;}}this.reverse();return idx;};
Array.prototype.contains = function(obj) {var i,listed=false;for(i=0;i<this.length;i++){if(this[i]==obj){listed=true;break;}}return listed;};

/**
 * Get Document Element URL.
 */
ZMI.prototype.get_document_element_url = function(url) {
	let i;
    if (url.indexOf('/content') >= 0) {
        i = url.indexOf('/content')+'/content'.length;
	}
    else if (url.indexOf('://') >= 0) {
        i = url.indexOf('://')+'://'.length;
        i = i+url.substr(i).indexOf('/');
}
    return url.substr(0,i);
}

/**
 * Get REST API URL.
 */
ZMI.prototype.get_rest_api_url = function(url) {
	const document_element_url = this.get_document_element_url(url);
	const i = document_element_url.length;
    return document_element_url+'/++rest_api'+url.substr(i);
}

/**
 * Parse url-params.
 */
ZMI.prototype.parseURLParams = function(url) {
	var qd = {};
	var search = url.indexOf("?")>0?url.substr(url.indexOf("?")):"?";
	search.substr(1).split("&").forEach(function(item) {
				var s = item.split("="),
					k = s[0],
					v = s[1] && decodeURIComponent(s[1]);
				(qd[k] = qd[k] || []).push(v);
			}
		);
	return qd;
}

var zmiParams;
$ZMI.registerReady(function(){
	// Parse params (?) and pseudo-params (#).
	zmiParams = {};
	var href = self.location.href;
	var base_url = href;
	var delimiter_list = ['?','#'];
	for (var h = 0; h < delimiter_list.length; h++) {
		var delimiter = delimiter_list[h];
		var i = base_url.indexOf(delimiter);
		if (i > 0) {
			base_url = base_url.substr(0,i);
		}
		var i = href.indexOf(delimiter);
		if (i > 0) {
			var query_string = href.substr(i+1);
			if (h < delimiter_list.length-1) {
				i = query_string.indexOf(delimiter_list[h+1]);
				if (i > 0) {
					query_string = query_string.substr(0,i);
				}
			}
			var l = query_string.split('&');
			for ( var j = 0; j < l.length; j++) {
				i = l[j].indexOf('=');
				if (i < 0) {
					break;
				}
				if (typeof zmiParams[l[j].substr(0,i)] == "undefined") {
					zmiParams[l[j].substr(0,i)] = unescape(l[j].substr(i+1));
				}
			}
		}
	}
	zmiParams['base_url'] = base_url;

	// Content-Editable ////////////////////////////////////////////////////////
	if (self.location.href.indexOf('/manage')>0 || self.location.href.indexOf('preview=preview')>0) {
		var hilight_css = `
			<style type="text/css">
				body:not(.zmi) .contentEditable.zmi-highlight:hover {
					cursor:pointer;
					background:unset !important;
					box-shadow: 0 0 0 1px black;
				}
				body:not(.zmi) .contentEditable.zmi-highlight:hover > * {
					transform:unset !important;
				}
				body:not(.zmi) .contentEditable.zmi-highlight:hover:before {
					content:" ";
					width:20px;
					height:20px;
					position:absolute;
					background-color:black;
					z-index:10;
					background-image: url("data:image/svg+xml;utf8,<svg width='20' height='20' viewBox='0 0 512 512' xmlns='http://www.w3.org/2000/svg'><circle fill='black' cx='256' cy='256' r='247.66' /><path d='m400 284c0 6.6-5.4 12-12 12h-92v92c0 6.6-5.4 12-12 12h-56c-6.6 0-12-5.4-12-12v-92h-92c-6.6 0-12-5.4-12-12v-56c0-6.6 5.4-12 12-12h92v-92c0-6.6 5.4-12 12-12h56c6.6 0 12 5.4 12 12v92h92c6.6 0 12 5.4 12 12z' fill='white'/></svg>");
				}
			</style>`;
		$('head').append(hilight_css);

		// PREVIEW CONTENTEDITABLE: It is recommended nesting the page content by an <article> element
		var page = $('.zms-page');
		var page_href = page.attr("data-absolute-url");
		var page_container_constructed = false;
		//debugger;
		if ( page.closest('article').length > 0 ) {
			page.closest('article').wrapInner('<div class="contentEditable zms-page" data-absolute-url="'+ page_href +'"></div>');
			page_container_constructed = true;
			// console.log('Page = article-Element');
		} else if ( page.closest('.article').length > 0 ) {
			page.closest('.article').wrapInner('<div class="contentEditable zms-page" data-absolute-url="'+ page_href +'"></div>');
			page_container_constructed = true;
			// console.log('Page = .article-Class');
		} else {
			page.siblings().first().wrapInner('<div class="contentEditable zms-page" data-absolute-url="'+ page_href +'"></div>');
			page_container_constructed = true;
			console.log('Page = 1st Sibling of Content Container; maybe use article-Element or .article-Class to mark the Content Container');
		}
		if ( page_container_constructed == false ) {
			console.log('Page-Container Not Found: Please Add article-Element or .article-Class to the HTML-Element that is Nesting the Page Content')
		}
		$('.contentEditable')
			.mouseover( function(evt) {
					evt.stopPropagation();
					$(this).addClass('zmi-highlight'); 
				})
			.mouseout( function(evt) {
					$(this).removeClass('zmi-highlight'); 
				})
			.click( function(evt) {
				evt.stopPropagation();
				if (evt.target != "undefined" && $.inArray(evt.target.nodeName.toLowerCase(),['a','button','input','select','textarea']) > -1) {
					return;
				}
				var href = $(this).attr("data-absolute-url");
				var lang = getZMILang();
				if (self.location.href.indexOf(href+'/manage_main')>=0 || evt.shiftKey==true) {
					href += '/manage_properties';
				}
				else {
					href += '/manage_main';
				}
				if (self.location.href.indexOf('/manage_translate')>0) {
					href += '_iframe';
					href += '?lang='+lang;
					href += '&ZMS_NO_BODY=1';
					$ZMI.iframe(href,{},{});
				}
				else if (self.location.href.indexOf('/manage')>0) {
					href += '?lang='+lang;
					self.location.href = href;
				}
				else {
					href += '?lang='+lang +'&preview=contentEditable';
					window.top.location.href = href;
				}
			})
			.attr( "title", "Click to Edit!\nShift+Click to Properties Menu");
	}

	// ZMS plugins
	if (typeof zmiParams['ZMS_HIGHLIGHT'] != 'undefined' && typeof zmiParams[zmiParams['ZMS_HIGHLIGHT']] != 'undefined') {
		$.plugin('zmi_highlight',{
			files: ['/++resource++zms_/jquery/plugin/jquery.plugin.zmi_highlight.js']
			});
		$.plugin('zmi_highlight').get('body',function(){});
	}
});

/**
 * Physical Path
 */
ZMI.prototype.getPhysicalPath = function() {
	var physical_path = $('meta[name="physical_path"]').attr('content');
	if (typeof physical_path == 'undefined') {
		physical_path = window.location.href;
	}
	return physical_path;
}

/**
 * Icon
 */
ZMI.prototype.icon = function(name,extra) {
	var tag = 'i';
	var icon = '<' + tag + ' class="' + this.icon_clazz(name) + '"';
	if (typeof extra != "undefined") {
		icon += ' ' + extra;
	}
	icon += '></' + tag + '>';
 	return icon;
}
ZMI.prototype.icon_clazz = function(name) {
	return name.replace(/icon-/,'fas fa-');
}
ZMI.prototype.icon_selector = function(name) {
	var tag = 'i';
	if (typeof name == "undefined") {
		return tag
	}
	return tag+'.'+this.icon_clazz(name).replace(/\s/gi,'.');
}

/**
 *  Wait cursor.
 */
var zmiCursor = [];
ZMI.prototype.setCursorWait = function(s) {
	if (zmiCursor.length == 0) {
		$("body").css("cursor","wait");
	}
	zmiCursor.push(s);
	console.log("setCursorWait[" + zmiCursor.length + "]: " + s);

}

ZMI.prototype.setCursorAuto = function() {
	zmiCursor.pop();
	if (zmiCursor.length == 0) {
		$("body").css("cursor","auto");
	}
}

/**
 * Returns language.
 */
function getZMILang() {
	if (typeof zmiParams['lang'] == 'undefined') {
    if (typeof zmiLangStr != "undefined") {
      zmiParams['lang'] = zmiLangStr['lang'];
    }
    if (typeof zmiParams['lang'] == 'undefined') {
      zmiParams['lang'] = 'eng';
    }
	}
	return zmiParams['lang'];
}

/**
 * Returns language-string for current manage-language.
 */
function getZMILangStr(key, data) {
	var langStr = $ZMI.getLangStr(key);
	if (typeof langStr=="undefined") {
		if (typeof zmiLangStr!="undefined") {
			langStr = zmiLangStr[key];
		}
		if (typeof langStr=='undefined') {
			langStr = key
		}
	}
	return langStr;
}

/**
 * Returns language-string for current content-language.
 */
ZMI.prototype.getLangStr = function(key, lang) {
	var k = "get_lang_dict";
	var v = this.getCachedValue(k);
	if (typeof v=="undefined") {
		var url = this.getBaseUrl();
		v = $.ajax({
			url: url+'/get_lang_dict',
			async: false
			}).responseJSON;
		this.setCachedValue(k,v);
	};
	if (typeof lang=="undefined") {
		lang = getZMILang();
	};
	var langStr;
	if (typeof v[key]!="undefined") {
		langStr = v[key][lang];
	};
	return langStr;
}

/**
 * Cache Ajax requests.
 */
ZMI.prototype.getCachedValue = function(k) {var v = localStorage["zmiCache["+k+"]"]; return typeof v=='undefined'?v:JSON.parse(v);}
ZMI.prototype.setCachedValue = function(k,v) {localStorage.setItem("zmiCache["+k+"]",JSON.stringify(v));return v;}

/**
 * Returns request-property.
 */
ZMI.prototype.getReqProperty = function(key, defaultValue) {
	var data  = {};
	data['key'] = key;
	if (typeof defaultValue != "undefined") {
		data['default'] = defaultValue;
	};
	var url = this.getPhysicalPath();
	if (url.indexOf('/content/')>0 || url.slice(-8)=='/content' ) {
		url = url.substr(0,url.indexOf('/content')+'/content'.length);
	} else {
		url='';
	};
	var r = $.ajax({
		url: url+'/getReqProperty',
		data: data,
		datatype: 'text',
		async: false
		}).responseText;
	return r;
}

/**
 *  Returns base-url.
 */
ZMI.prototype.getBaseUrl = function(key, defaultValue) {
		var url = this.getPhysicalPath();
		if (url.indexOf('/content/')>0 || url.slice(-8)=='/content' ) {
			url = url.substr(0,url.indexOf('/content')+'/content'.length);
		} else {
			url='';
		};
		return url;
}

/**
 * Returns conf-property.
 */
ZMI.prototype.getConfProperty = function(key, defaultValue) {
	var r = this.getCachedValue(key);
	if (typeof r=="undefined") {
		var data  = {};
		data['key'] = btoa(key);
		if (typeof defaultValue != "undefined") {
			data['default'] = defaultValue;
		};
		var url = this.getBaseUrl();
		var r = $.ajax({
			url: url+'/getConfProperty',
			data: data,
			datatype: 'text',
			headers: {'Cache-Control':'max-age=1800','X-Accel-Expires':1800},
			async: false
			}).responseText;
		this.setCachedValue(key,r);
	}
	return r;
}

/**
 * Returns conf-properties.
 */
ZMI.prototype.getConfProperties = function(prefix) {
	var r = this.getCachedValue(prefix);
	if (typeof r=="undefined") {
		var data  = {};
		data['prefix'] = btoa(prefix);
		var url = this.getBaseUrl();
		var r = $.ajax({
			url: url+'/getConfProperties',
			data: data,
			datatype: 'text',
			async: false
			}).responseText;
		this.setCachedValue(prefix,r);
	}
	return eval("("+r+")");
}

/**
 * Returns display-icon.
 */
ZMI.prototype.display_icon = function(meta_type) {
	var k = "display_icon."+meta_type;
	var v = this.getCachedValue(k);
	if (typeof v=="undefined") {
		var data  = {}
		data['meta_type'] = meta_type;
		var url = this.getPhysicalPath();
		if (url.indexOf('/content/')>0 || url.slice(-8)=='/content' ) {
			url = url.substr(0,url.indexOf('/content')+'/content'.length);
		} else {
			url='';
		}
		v = $.ajax({
			url: url+'/display_icon',
			data: data,
			datatype: 'text',
			async: false
			}).responseText;
	}
	return this.setCachedValue(k,v);
}

/**
 *Decode HTML-Entities.
 */
ZMI.prototype.HTMLDecode = function(str) {
	var char_names = {
		'Auml':'\u00C4',
		'Ouml':'\u00D6',
		'Uuml':'\u00DC',
		'auml':'\u00E4',
		'ouml':'\u00F6',
		'uuml':'\u00FC',
		'szlig':'\u00DF'
		};
	for (var char_name in char_names) {
		var char_code = char_names[char_name].toString(16);
		var re = new RegExp("&"+char_name+";","g");
		str = str.replace(re,char_code);
	}
	return str;
}

/**
 * Copy to clipboard.
 */
ZMI.prototype.CopyToClipboard = function(str) {
	var $temp = $("<textarea></textarea>");
	$("body").append($temp);
	try {
		$temp.val(str).select();
		document.execCommand("copy");
	} catch (e) {
	}
	$temp.remove();
}

/**
 * $: Register 
 */
if (typeof $ != "undefined") {
	$ZMI.runReady();
}