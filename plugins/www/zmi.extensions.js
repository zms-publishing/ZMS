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

var zmiParams = {};

$(function(){
	// Parse params (?) and pseudo-params (#).
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
	zmiParams['URL'] = base_url;
	if (typeof zmiParams['zmi-debug'] != "undefined") {
		$ZMI.toggleDebug(true);
	}

	$ZMI.setCursorWait("BO zmi.extensions");

	// Execute registered onReady-callbacks.
	$ZMI.writeDebug("zmi.extensions: Execute registered onReady-callbacks.");
	$ZMI.runReady();

	// Content-Editable ////////////////////////////////////////////////////////
	if (self.location.href.indexOf('/manage')>0 || self.location.href.indexOf('preview=preview')>0) {
		$('.contentEditable,.zmiRenderShort')
			.mouseover( function(evt) {
				$(this).addClass('preview').addClass('highlight'); 
			})
			.mouseout( function(evt) {
				$(this).removeClass('preview').removeClass('highlight'); 
			})
			.click( function(evt) {
				evt.stopPropagation();
				var href = ""+self.location.href;
				if (href.indexOf('?')>0) {
					href = href.substr(0,href.indexOf('?'));
				}
				if (href.lastIndexOf('/')>0) {
					href = href.substr(0,href.lastIndexOf('/'));
				}
				var lang = null;
				var parents = $(this).parents('.contentEditable');
				for ( var i = 0; i <= parents.length; i++) {
					var pid;
					if ( i==parents.length) {
						pid = $(this).attr('id');
					}
					else {
						var $el = $(parents[parents.length-i-1]);
						if ($el.hasClass("portalClient")) {
							if (href.lastIndexOf('/')>0) {
								href = href.substr(0,href.lastIndexOf('/'));
							}
						}
						pid = $el.attr('id');
					}
					if (pid.length > 0) {
						if (lang == null) {
							lang = pid.substr(pid.lastIndexOf('_')+1);
						}
						pid = pid.substr(pid.indexOf('_')+1);
						if(pid.substr(pid.length-('_'+lang).length)==('_'+lang)) {
							pid = pid.substr(0,pid.length-('_'+lang).length);
						}
						if (!href.endsWith('/'+pid)) {
							href += '/'+pid;
						}
					}
				}
				if (self.location.href.indexOf(href+'/manage_main')==0) {
					href += '/manage_properties';
				}
				else {
					href += '/manage_main';
				}
				if (self.location.href.indexOf('/manage_translate')>0) {
					href += '_iframe';
					href += '?lang='+lang;
					href += '&ZMS_NO_BODY=1';
					zmiIframe(href,{},{});
				}
				else if (self.location.href.indexOf('/manage')>0) {
					href += '?lang='+lang;
					self.location.href = href;
				}
				else {
					href += '_iframe';
					href += '?lang='+lang;
					showFancybox({
						'autoDimensions':false,
						'hideOnOverlayClick':false,
						'href':href,
						'transitionIn':'fade',
						'transitionOut':'fade',
						'type':'iframe',
						'width':819
					});
				}
			})
		.attr( "title", "Click to edit!");
	}
	// ZMS plugins
	if (typeof zmiParams['ZMS_HIGHLIGHT'] != 'undefined' && typeof zmiParams[zmiParams['ZMS_HIGHLIGHT']] != 'undefined') {
		$.plugin('zmi_highlight',{
			files: ['/++resource++zms_/jquery/plugin/jquery.plugin.zmi_highlight.js']
			});
		$.plugin('zmi_highlight').get('body',function(){});
	}

	$ZMI.setCursorAuto("EO zmi.extensions");
});

/**
 * Physical Path
 */
ZMI.prototype.getPhysicalPath = function() {
	return $('meta[name="physical_path"]').attr('content');
}

/**
 * Icon
 */
ZMI.prototype.icon = function(name,extra) {
	var tag = 'i';
	var icon = '<' + tag + ' class="' + $ZMI.icon_clazz(name) + '"';
	if (typeof extra != "undefined") {
		icon += ' ' + extra;
	}
	icon += '></' + tag + '>';
 	return icon;
}
ZMI.prototype.icon_clazz = function(name) {
	return name;
}
ZMI.prototype.icon_selector = function(name) {
	var tag = 'i';
	if (typeof name == "undefined") {
		return tag
	}
	return tag+'.'+$ZMI.icon_clazz(name);
}

/**
 * Debug
 */
ZMI.prototype.toggleDebug = function(b) {
	var $div = $("div#zmi-debug");
	if ($div.length==0) {
		$("body").append('<div id="zmi-debug"></div>');
		$div = $("div#zmi-debug");
	}
	if (b) {
		$div.css("display","block");
	}
	else {
		$div.css("display","none");
	}
};
ZMI.prototype.writeDebug = function(s) {
	var $div = $("div#zmi-debug");
	if ($div.css("display")!="none") {
		var d = new Date();
		$div.html("<code>["+(d)+'...'+(d.getMilliseconds())+"] "+s+'</code><br/>'+$div.html());
	}
};

/**
 *  Wait cursor.
 */
var zmiCursor = [];
ZMI.prototype.setCursorWait = function(s) {
	if (zmiCursor.length == 0) {
		$("body").css("cursor","wait");
	}
	zmiCursor.push(s);
	$ZMI.writeDebug(">>>> " + zmiCursor.join(" > "));
}

ZMI.prototype.setCursorAuto = function() {
	$ZMI.writeDebug("<<<< " + zmiCursor.join(" > "));
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
ZMI.prototype.getConfProperty = function(key, defaultValue) {
	var data  = {}
	data['key'] = key;
	if (typeof defaultValue != "undefined") {
		data['default'] = defaultValue;
	}
	var url = zmiParams['URL'];
	if (url.indexOf('/content/')>0) {
		url = url.substr(0,url.indexOf('/content/')+'/content/'.length);
	}
	return $.ajax({
		url: url+'getConfProperty',
		data: data,
		datatype: 'text',
		async: false
		}).responseText;
}
