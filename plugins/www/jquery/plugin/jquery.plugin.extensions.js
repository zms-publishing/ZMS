/*
 * @see http://nicolas.rudas.info/jQuery/getPlugin/
 */

/*
 * Defaults
 */

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
	// Parse params.
	var href = self.location.href;
	var i = href.indexOf('?');
	href = href.substr(i+1);
	var l = href.split('&');
	for ( var j = 0; j < l.length; j++) {
		i = l[j].indexOf('=');
		zmiParams[l[j].substr(0,i)] = unescape(l[j].substr(i+1));
	}
	// Content-Editable ////////////////////////////////////////////////////////
	if (self.location.href.indexOf('/manage')>0 || self.location.href.indexOf('preview=preview')>0) {
		$('.contentEditable,.zmiRenderShort')
			.mouseover( function(evt) {
				$(this).addClass('preview').addClass('highlight'); 
			})
			.mouseout( function(evt) {
				$(this).removeClass('preview').removeClass('highlight'); 
			})
			.dblclick( function(evt) {
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
						pid = $(parents[parents.length-i-1]).attr('id');
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
				href += '/manage_main';
				if (self.location.href.indexOf('/manage_translate')>0) {
					href += '_iframe';
					href += '?lang='+lang;
					href += '&ZMS_NO_BODY=1';
					zmiIframe(href,{},{});
				}
				else if (self.location.href.indexOf('/manage')>0) {
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
		.attr( "title", "Double-click to edit!");
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
 * jQuery UI
 * @see http://jqueryui.com
 */
$(function(){
	$('body.zmi').each(function(){
		initUI(this);
	});
});

function initUI(context) {
	// Icons:
	// hover states on the static widgets
	$('ul#icons li,ul.zmi-icons li,div.zmi-icon',context).hover(
		function() {
			if ($(this).hasClass('ui-state-default')) {
				$(this).addClass('ui-state-hover');
			}
		},
		function() {
			if ($(this).hasClass('ui-state-default')) {
				$(this).removeClass('ui-state-hover');
			}
		}
	);
	pluginUIDatepicker('input.datepicker,input.datetimepicker',function(){
		// Date-Picker
		$.datepicker.setDefaults( $.datepicker.regional[ pluginLanguage()]);
		$('input.datepicker',context).datepicker({
				showWeek: true
			});
		$('input.datetimepicker',context).datepicker({
				showWeek: true,
				beforeShow: function(input, inst) {
						var v = $(input).val();
						var e = '';
						var i = v.indexOf(' ');
						if ( i > 0) {
							e = v.substr(i+1);
							v = v.substr(0,i);
						}
						$(inst).data("inputfield",input);
						$(inst).data("extra",e);
					},
				onClose: function(dateText, inst) {
						if (dateText) {
							var input = $(inst).data("inputfield");
							var e = $(inst).data("extra");
							if (e) {
								$(input).val(dateText+" "+e);
							}
						}
					}
			});
	});
	return context;
}

function pluginLanguage() {
	return getZMILangStr('LOCALE',{'nocache':""+new Date()});
}

function pluginUIDatepicker(s, c) {
	var lang = pluginLanguage();
	$.plugin('ui_datepicker',{
		files: [
				'/++resource++zms_/jquery/ui/i18n/jquery.ui.datepicker-'+lang+'.js'
		]});
	$.plugin('ui_datepicker').get(s,c);
}

function zmiAutocompleteDefaultFormatter(l, q) {
	return $.map(l,function(x){
		return {label: x.replace(
								new RegExp(
										"(?![^&;]+;)(?!<[^<>]*)(" +
										$.ui.autocomplete.escapeRegex(q) +
										")(?![^<>]*>)(?![^&;]+;)", "gi"
										), "<strong>$1</strong>" ),
						value: x};
						})
}

function zmiAutocomplete(s, o) {
	$(s).autocomplete(o)
	.data( "autocomplete" )._renderItem = function( ul, item ) {
			return $( "<li></li>" )
				.data( "item.autocomplete", item )
				.append( "<a>" + item.label + "</a>" )
				.appendTo( ul );
	};
}


/**
 * Fancybox
 * @see http://fancybox.net/
 */
var pluginFancyboxDefaultOptions = {
			'autoScale'		: false,
			'titleShow'		: false,
			'hideOnContentClick': true,
			'transitionIn'	: 'elastic',
			'transitionOut'	: 'elastic'
		};

$(function(){
	$('a.fancybox')
		.click(function() {
			pluginFancyboxDefaultOptions['href'] = $(this).attr('href');
			// Ensure that this link will be opened as an image!
			if ($("img.img",this).length==1) {
				pluginFancyboxDefaultOptions['type'] = 'image';
			}
			return showFancybox(pluginFancyboxDefaultOptions);
		});
});

function pluginFancybox(s, c) {
	$.plugin('fancybox',{
		files: ['/++resource++zms_/jquery/fancybox/jquery.easing-1.3.pack.js',
				'/++resource++zms_/jquery/fancybox/jquery.mousewheel-3.0.4.pack.js',
				'/++resource++zms_/jquery/fancybox/jquery.fancybox-1.3.4.pack.js',
				'/++resource++zms_/jquery/fancybox/jquery.fancybox-1.3.4.css']
		});
	$.plugin('fancybox').get(s,c);
}

function showFancybox(p) {
	pluginFancybox('body',function() {
		$.fancybox(p);
		try {
			$("#fancybox-wrap").draggable();
		}
		catch(e) {
		}
	});
	return false;
}


/**
 * Autocomplete
 * @see http://bassistance.de/jquery-plugins/jquery-plugin-autocomplete/
 * @deprecated
 */
function pluginAutocomplete(s, c) {
	$.plugin('autocomplete',{
		files: ['/++resource++zms_/jquery/autocomplete/jquery.bgiframe.min.js',
				'/++resource++zms_/jquery/autocomplete/jquery.autocomplete.min.js',
				'/++resource++zms_/jquery/autocomplete/jquery.autocomplete.css']
	});
	$.plugin('autocomplete').get(s,c);
}


/**
 * jQuery Editable Combobox (jEC)
 * @see http://code.google.com/p/jquery-jec/
 */
function pluginJEC(s, c) {
	$.plugin('jec',{
		files: ['/++resource++zms_/jquery/jec/jquery.jec.min-0.5.2.js']
	});
	$.plugin('jec').get(s,c);
}


/**
 * Jcrop - the jQuery Image Cropping Plugin
 * @see http://deepliquid.com/content/Jcrop.html
 */
function runPluginJcrop(c) {
	$.plugin('jcrop',{
		files: ['/++resource++zms_/jquery/jcrop/jquery.Jcrop.min.js',
				'/++resource++zms_/jquery/jcrop/jquery.Jcrop.css']
		});
	$.plugin('jcrop').get('body',c);
}

/**
 * jQuery Cookies
 * @see http://code.google.com/p/cookies
 */
function runPluginCookies(c) {
	$.plugin('cookies',{
		files: ['/++resource++zms_/jquery/jquery.cookies.2.1.0.min.js']
		});
	$.plugin('cookies').get('body',c);
}

/**
 * jQuery JSON
 */
function runPluginJSON(c) {
	$.plugin('json',{
		files: ['/++resource++zms_/jquery/jquery.json-2.2.min.js']
		});
	$.plugin('json').get('body',c);
}
