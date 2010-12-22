jQuery.fn.datetimepicker = function() {

	var opt = arguments[0] || {};

	return this.each(function(){

			function initDatetimePickerPlug(opt) {
				if (!$('#datetimepicker').length) {
					var htmlins = '<div id="datetimepicker"></div>';
					$('body').append(htmlins);
					opt['onSelect'] = function(dateText, inst) {
								$($('#datetimepicker').data('inputfield')).val(
											dateText+$('#datetimepicker').data('extra')
								);
								$('#datetimepicker').hide('normal');
							};
					$('#datetimepicker').datepicker(opt);
					$('#datetimepicker').mousedown(clickDatetimePickerPlug);
					$(document).mousedown(closeDatetimePickerPlug);
				}
			}

			$(this).bind('focus',function(){ 
				var top 	= $(this).offset().top+$(this).outerHeight(); 
				var left 	= $(this).offset().left;
				initDatetimePickerPlug(opt);
				parseDatetimePickerPlug(this);
				$('#datetimepicker').css({
									position: 'absolute',
									left: left+'px',
									top: top+'px'
									}).show('normal');
				$('#datetimepicker').data('inputfield',this);
			});

			function parseDatetimePickerPlug(obj) {
				var v = $(obj).val();
				var e = '';
				var i = v.indexOf(' ');
				if ( i > 0) {
					e = v.substr(i);
					v = v.substr(0,i);
				}
				$('#datetimepicker').data('extra',e);
				var d = new Date();
				var df = $.datepicker.regional[ pluginLanguage()]['dateFormat'];
				if (v) {
					d = $.datepicker.parseDate(df,v);
				}
				$('#datetimepicker').datepicker('setDate',d);
			}

			function clickDatetimePickerPlug(e) {
				var event = e || window.event;
				if (event.stopPropagation) {
					event.stopPropagation();
				} else {
					event.cancelBubble = true;
				}
			}

			function closeDatetimePickerPlug(event) {
				$('#datetimepicker').hide('normal');
			}

		});
}