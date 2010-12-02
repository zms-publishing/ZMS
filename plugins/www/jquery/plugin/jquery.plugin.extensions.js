/*
 * @see http://nicolas.rudas.info/jQuery/getPlugin/
 */

/*
 * Defaults
 */
$(function(){
	$.plugin('zms',{
		files: ['/++resource++zms_/jquery/jquery.cookies.2.1.0.min.js',
				'/++resource++zms_/jquery/jquery.dimensions.1.2.0.min.js']
		});
	// Always load
	$.plugin('zms').get('body',function(){
		// Content-Editable ////////////////////////////////////////////////////////
		if (self.location.href.indexOf('/manage')>0 || self.location.href.indexOf('preview=preview')>0) {
			pluginFancybox('.contentEditable',function() {});
			$('.contentEditable,.zmiRenderShort')
				.mouseover( function(evt) {
					$(this).addClass('preview').addClass('highlight'); 
				})
				.mouseout( function(evt) {
					$(this).removeClass('preview').removeClass('highlight'); 
				})
				.dblclick( function(evt) {
					evt.stopPropagation();
					var href = self.location.href;
					if (href.indexOf('?')>0) {
						href = href.substr(0,href.indexOf('?'));
					}
					if (href.lastIndexOf('/')>0) {
						href = href.substr(0,href.lastIndexOf('/'));
					}
					var parents = $(this).parents('.contentEditable,.zmiRenderShort');
					for ( var i = 0; i < parents.length; i++) {
						var pid = $(parents[i]).attr('id');
						pid = pid.substr(pid.indexOf('_')+1);
						href += '/'+pid;
					}
					var pid = $(this).attr('id');
					var lang = pid.substr(pid.lastIndexOf('_')+1);
					pid = pid.substr(pid.indexOf('_')+1,pid.lastIndexOf('_')-pid.indexOf('_')-1);
					href += '/'+pid;
					href += '/manage_main';
					if (self.location.href.indexOf('/manage')>0
						&& self.location.href.indexOf('/manage_translate')<0) {
						self.location.href = href;
					}
					else {
						href += '_iframe';
						href += '?lang='+lang;
						$.fancybox({
							'autoDimensions':false,
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
		////////////////////////////////////////////////////////////////////////////
	});
});


/* jQuery UI
 * @see http://jqueryui.com
 */
$(function(){
	// Always load
	pluginUI('body',function(){});
	// Icons
	pluginUI('ul#icons',function() {
		// apply minimum-width to avoid line-breaks
		var uls = $('ul#icons');
		for ( var i = 0; i < uls.length; i++) {
			var ul = $(uls[i]);
			var lis = $('li',ul);
			ul.css('min-width',lis.length*$(lis[0]).outerWidth());
		}
		// hover states on the static widgets
		$('ul#icons li').hover(
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
	});
	// Date-Picker
	pluginUI('input.datepicker',function() {
		$.datepicker.setDefaults( $.datepicker.regional[ pluginLanguage()]);
		$('input.datepicker').datepicker({
			'showWeek'	: true
		});
	});
});

function pluginLanguage() {
	var lang = window.navigator.language;
	if (typeof lang == 'undefined') {
		lang = window.navigator.userLanguage
	}
	if (lang.indexOf('-') > 0) {
		lang = lang.substr(0,lang.indexOf('-'));
	}
	return lang;
}

function pluginUI(s, c) {
	$.plugin('ui',{
		files: ['/++resource++zms_/jquery/ui/js/jquery-ui-1.8.6.custom.min.js',
				'/++resource++zms_/jquery/ui/i18n/jquery.ui.datepicker-'+pluginLanguage()+'.js'
		]});
	$.plugin('ui').get(s,c);
}


/* Fancybox
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
	pluginFancybox('a.fancybox',function() {
		$('a.fancybox').fancybox(pluginFancyboxDefaultOptions);
	});
});

function pluginFancybox(s, c) {
	$.plugin('fancybox',{
		files: ['/++resource++zms_/jquery/fancybox/jquery.easing-1.3.pack.js',
				'/++resource++zms_/jquery/fancybox/jquery.fancybox-1.3.1.pack.js',
				'/++resource++zms_/jquery/fancybox/jquery.fancybox-1.3.1.css']
		});
	$.plugin('fancybox').get(s,c);
}


/* Autocomplete
 * @see http://bassistance.de/jquery-plugins/jquery-plugin-autocomplete/
 */
function pluginAutocomplete(s, c) {
	$.plugin('autocomplete',{
		files: ['/++resource++zms_/jquery/autocomplete/jquery.bgiframe.min.js',
				'/++resource++zms_/jquery/jquery.dimensions.1.2.0.min.js',
				'/++resource++zms_/jquery/autocomplete/jquery.autocomplete.min.js',
				'/++resource++zms_/jquery/autocomplete/jquery.autocomplete.css']
	});
	$.plugin('autocomplete').get(s,c);
}


/* jQuery Editable Combobox (jEC)
 * @see http://code.google.com/p/jquery-jec/
 */
function pluginJEC(s, c) {
	$.plugin('jec',{
		files: ['/++resource++zms_/jquery/jec/jquery.jec.min-0.5.2.js']
	});
	$.plugin('jec').get(s,c);
}


/* Jcrop - the jQuery Image Cropping Plugin
 * @see http://deepliquid.com/content/Jcrop.html
 */
function pluginJcrop(s, c) {
	$.plugin('jcrop',{
		files: ['/++resource++zms_/jquery/jcrop/jquery.Jcrop.min.js',
				'/++resource++zms_/jquery/jcrop/jquery.Jcrop.css']
		});
	$.plugin('jcrop').get(s,c);
}
