/*
 * @see http://nicolas.rudas.info/jQuery/getPlugin/
 */
 
function pluginLanguage() {
	return getZMILangStr('LOCALE',{'nocache':""+new Date()});
}

/**
 * jQuery UI
 */
function pluginUI(s, c) {
	//$ZMI.setCursorWait("pluginUI");
	$.plugin('ui',{
		files: [
				$ZMI.getConfProperty('jquery.ui'),
				$ZMI.getConfProperty('zmi.ui')
		]});
	$.plugin('ui').get(s,function(){
			//$ZMI.setCursorAuto("pluginUI");
			c();
		});
}

/**
 * jQuery UI Datepicker
 */
function pluginUIDatepicker(s, c) {
	//$ZMI.setCursorWait("pluginUIDatepicker");
	var lang = pluginLanguage();
	$.plugin('ui_datepicker',{
		files: [
				'/++resource++zms_/jquery/ui/i18n/jquery.ui.datepicker-'+lang+'.js'
		]});
	pluginUI(s,function() {
			//$ZMI.setCursorAuto("pluginUIDatepicker");
			$.plugin('ui_datepicker').get(s,c);
		});
}

/**
 * jQuery UI Autocomplete
 */
function zmiAutocompleteDefaultFormatter(l, q) {
	return $.map(l,function(x){
		var label = x;
		var value = x;
		if (typeof x == "object") {
			label = x.label;
			value = x.value;
		}
		var orig = label;
		return {label: label.replace(
								new RegExp(
										"(?![^&;]+;)(?!<[^<>]*)(" +
										$.ui.autocomplete.escapeRegex(q) +
										")(?![^<>]*>)(?![^&;]+;)", "gi"
										), "<strong>$1</strong>" ),
				value: value,
				orig: label};
			})
}

function zmiAutocomplete(s, o) {
	//$ZMI.setCursorWait("zmiAutocomplete");
	pluginUI(s,function() {
		//$ZMI.setCursorAuto("zmiAutocomplete");
		$(s).autocomplete(o)
		.data("ui-autocomplete")._renderItem = function( ul, item ) {
				return $( "<li></li>" )
					.data( "item.autocomplete", item )
					.append( "<a>" + item.label + "</a>" )
					.appendTo( ul );
			};
	});
}


/**
 * ZMSLightbox
 */
$(function(){
	$('a.zmslightbox,a.fancybox')
		.each(function() {
				var $img = $("img",$(this));
				$img.attr("data-hiresimg",$(this).attr("href"));
				$(this).click(function() {
						return showFancybox($img);
					});
			});
});

function pluginFancybox(s, c) {
	$.plugin('zmslightbox',{
		files: ['/++resource++zms_/jquery/zmslightbox/zmslightbox.js?ts='+new Date(),
				'/++resource++zms_/jquery/zmslightbox/zmslightbox.css?ts='+new Date()]
		});
	$.plugin('zmslightbox').get(s,c);
}

function showFancybox($sender) {
	pluginFancybox('body',function() {
			show_zmslightbox($sender);
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
 * jQuery JSON
 */
function runPluginJSON(c) {
	$.plugin('json',{
		files: ['/++resource++zms_/jquery/jquery.json-2.2.min.js']
		});
	$.plugin('json').get('body',c);
}
