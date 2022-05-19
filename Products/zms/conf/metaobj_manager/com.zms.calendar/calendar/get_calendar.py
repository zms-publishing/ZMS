## Inspired by https://www.huiwenteo.com/normal/2018/07/24/django-calendar.html

import locale
## IMPORTANT NOTE: first install your OS locale pack, e.g.
## sudo apt-get install language-pack-de-base

from datetime import datetime, timedelta
import dateutil.parser as dparser
from calendar import HTMLCalendar

## EVENT DATA MODEL
# events = [
# 	{
# 		'start_time':'2022-05-18 15:00',
# 		'end_time':'2022-05-18 18:00',
# 		'title':'Exam of Economics 1st Semester Part 1',
# 		'description':'Its gonna be hard, but not impossible',
# 		'url':'https://exam.yeepa-formosa.net/',
# 	},
# 	{
# 		'start_time':'2022-05-20 15:00',
# 		'end_time':'2022-05-20 18:00',
# 		'title':'Exam of Economics 1st Semester Part 2',
# 		'description':'Its gonna be hard and impossible',
# 		'url':'https://exam.yeepa-formosa.net/',
#
# 	}
# ]


# SET LOCALE
locale.setlocale(locale.LC_ALL, 'de_DE.UTF-8')

# HELPERS
def parse_dt(s='2022-05-20 18:00'):
	return dparser.parse(s).date()

def filter_events_by_date(events, year, month, day):
	this_dt = datetime(year, month, day).date()
	return [e for e in events if parse_dt(e.get('start_time',''))==this_dt]

# FUNCTION OVERWRITE OF formatday()
class Calendar(HTMLCalendar):
	def __init__(self, year=None, month=None, events=[]):
		self.year = year
		self.month = month
		self.events = events
		super(Calendar, self).__init__()

	# formats a day as a td
	# filter events by day
	def formatday(self, day, weekday):
		"""
		Return a day as a table cell.
		"""
		if day == 0:
			# day outside month
			return '<td class="%s">&nbsp;</td>' % (self.cssclass_noday)
		else:
			events_dt = filter_events_by_date(self.events, self.year, self.month, day)
			t_short = ''
			t_long = ''
			event_link = ''
			has_events = False
			if events_dt:
				has_events = True
				event_id = [e.get('col_id','') for e in events_dt][0]
				event_link = 'onclick="document.getElementById(\'%s\').classList.add(\'hilight\');$(\'html,body\').animate({scrollTop:$(\'#%s\').offset().top}, 600)"'%(event_id,event_id)
				events_titles = [(e.get('start_time','').split(' ')[-1] == '00:00' and e.get('title','') or '%s | %s'%(e.get('start_time','').split(' ')[-1], e.get('title',''))) for e in events_dt]
				events_titles_long = ['%s : %s'%(e.get('title',''), e.get('description','')) for e in events_dt]
				t_short = '<br/>'.join(events_titles)
				t_long = '\n'.join(events_titles_long)
		# return '<td class="%s">%d</td>' % (self.cssclasses[weekday], day)
		return '<td %s class="%s" %s title="%s"><span class="day">%d</span> %s</td>' % (event_link, self.cssclasses[weekday], has_events and 'data-toggle="tooltip"' or '',  t_long, day, has_events and '<p><i class="far fa-calendar text-info"></i> %s</p>'%(t_short) or '<p></p>')


def get_calendar(self,year=2000,month=1,events=[]):
	htmlcal = Calendar(year=year,month=month,events=events)
	htmlcal.cssclasses = [style + ' text-nowrap' for style in HTMLCalendar.cssclasses]
	htmlcal.cssclass_month = "month table table-bordered"
	htmlcal.cssclass_month_head = "month-head text-center"
	# htmlcal.cssclass_year = "text-italic lead"
	return htmlcal.formatmonth(htmlcal.year, htmlcal.month)
