// ############################################################################
// ### Notification Service
// ############################################################################

function zmiGetNotifications() {
	$.get('getNotifications',
		{},
		function(data) {
			var notifications = eval('('+data+')');
			var maxseverity = null;
			var html = '';
			for ( var i = 0; i < notifications.length; i++) {
				var notification = notifications[i];
				var severity = notification['severity'];
				html += '<div class="form-label">Current Messages:</div>';
				html += '<div class="form-small">';
				html += '<img src="/misc_/zms/ico_'+severity+'.gif" alt="" border="0" align="absmiddle"/> ';
				html += '<strong>'+notification['date']+'</strong> ';
				html += notification['html'];
				html += '</div>';
				if ((maxseverity == null)
					|| (severity == 'warning' && (maxseverity == 'info'))
					|| (severity == 'warning' && (maxseverity == 'info' || maxseverity == 'warning'))) {
					maxseverity = severity;
				}
			}
			if (maxseverity != null) {
				if ( $('#ZMIManageTabsButtons > li#ZMIManageTabsNotifications').length==0) {
					$('#ZMIManageTabsButtons').html('<li id="ZMIManageTabsNotifications"></li>'+$('#ZMIManageTabsButtons').html());
				}
				$('#ZMIManageTabsButtons > li#ZMIManageTabsNotifications').html(
					'<a href="#ZMIManageTabsNotificationsDiv"><img src="/misc_/zms/ico_'+maxseverity+'.gif" title="Click to open notifications..." border="0"></a>'+
					'<div style="display:none">'+
					'<div id="ZMIManageTabsNotificationsDiv">'+
					html+
					'</div>'+
					'</div>'+
					'');
				pluginFancybox('a[href=#ZMIManageTabsNotificationsDiv]',function() {
					$('a[href=#ZMIManageTabsNotificationsDiv]').fancybox({
						});
					});
			}
			setTimeout('zmiGetNotifications()',5000);
		});
}
function zmiClearNotifications() {
}
$(function() {
	pluginFancybox('body',function() {});
	zmiGetNotifications();
});

// ############################################################################
// ### Date Functions
// ############################################################################

/**
 * y2k
 */
function y2k(number) {
    rtn = number;
    if (rtn>=0 && rtn<50)
        rtn += 2000;
    else
    if (rtn>=50 && rtn<100)
        rtn += 1900;
    return (rtn < 1000) ? rtn + 1900 : rtn;
}

/**
 * isDate:
 *
 * checks if date passed is valid
 * will accept dates in following format:
 * isDate(dd,mm,ccyy), or
 * isDate(dd,mm) - which defaults to the current year, or
 * isDate(dd) - which defaults to the current month and year.
 * Note, if passed the month must be between 1 and 12, and the
 * year in ccyy format.
 */
function isDate (day,month,year) {
     var today = new Date();
     year = ((!year) ? y2k(today.getYear()):year);
     month = ((!month) ? today.getMonth():month-1);
     if (!day) return false
     var test = new Date(year,month,day);
     if ( (y2k(test.getYear())==year || y2k(test.getYear())==year+1900 || y2k(test.getYear())==year+2000) &&
          (month == test.getMonth()) &&
          (day == test.getDate()) )
     {
         return true;
     } else
     {
         return false;
     }
}

/**
 * parseDateInt:
 */
function parseDateInt(s) {
  while (s.length > 0 && s.indexOf("0") == 0)
    s = s.substring(1);
  if (s.length == 0)
    return 0;
  else
    return parseInt(s);
}

/**
 * validDate:
 */
function validDate(s) {
  return (getDate(s) != null)
}

/**
 * getDate:
 */
function getDate(s) {
  var now = new Date();
  var day = now.getDate();
  var month = now.getMonth()+1;
  var year = now.getYear();
  var daySep = s.indexOf(".",0);
  if (daySep >= 0) {
    var monthSep = s.indexOf( "." , daySep + 1 );
    if (monthSep >= 0) {
        day   = parseDateInt(s.substring( 0 , daySep ));
        month = parseDateInt(s.substring( daySep + 1 , monthSep ));
        year  = parseDateInt(s.substring( monthSep + 1 ));
    } else {
        day = parseDateInt(s.substring( 0 , daySep ));
        month = parseDateInt(s.substring( daySep + 1 ));
    }
  } else
     day = parseDateInt(s);

  if (isNaN(day) || isNaN(month) || isNaN(year))
      return null
  else {
      if (!isDate(day,month,year))
         return null;
      else {
         month = month-1;
         year = y2k(year);
         return new Date(year,month,day);
      }
  }
}
