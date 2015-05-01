import datetime
from optparse import make_option

from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone

from dhis2 import models as dhis2
from django_ccem import models as ccem
from util.xlsxreport import Report

import json
import code

class Command(BaseCommand):
	
	help = 'export all messages to json'
	
	option_list = BaseCommand.option_list + (
		make_option('-s','--start',help='Start date for message export yy-mm-dd must be used with --end'),
		make_option('-e','--end',help='End date for message export yy-mm-dd must be used with --start'),
		make_option('-c','--count',action='store_true',default=False,help='Display message count'),
		make_option('-m','--month',default='',help='Set start and end month YYYY-MM or OFFSET in the past'),
		make_option('-a','--all',action='store_true',default=False,help='Set start and end so all messages are processed'),
		make_option('-t','--type',choices=('json','xlsx'),default='json',help='Output type'), 
	)
	
	def handle(self,*args,**kwargs):
		
		start,end = get_date_range(kwargs)
	
		raw_messages = ccem.Message.objects.filter(is_submission=True,has_error=False,created__range=(start,end))
		
		if kwargs['count']:
			self.stdout.write('Messages: %i'%raw_messages.count())
			return
			
		output = make_json(raw_messages) if kwargs['type'] == 'json' else make_xlsx(raw_messages)
			
		print output
		
'''
Utility Functions
'''

def get_date_range(kwargs):
	if kwargs['all']: #set start and end for all messages
		start = datetime.date(2013,7,1)
		end = datetime.date.today()
		
	elif kwargs['start'] and kwargs['end']: #set start and end
		start = parse_date(kwargs['start'])
		end = parse_date(kwargs['end'])
		
	else:
		if not kwargs['month'] or kwargs['month'].isdigit(): #offset not set or is OFFSET in the past
			today = datetime.date.today()
			offset = 0 if not kwargs['month'].isdigit() else int(kwargs['month'])
			month = datetime.date(today.year-offset/12,today.month-offset%12,1)
		else: #assume month is in YYYY-MM format
			year,month = kwargs['month'].split()
			month = datetime.date(int(year),int(month),1)
		start = month - datetime.timedelta(days=3)
		end = month + datetime.timedelta(days=10)
			
	start = datetime.datetime.combine(start,datetime.time(tzinfo=timezone.utc))
	end = datetime.datetime.combine(end,datetime.time(tzinfo=timezone.utc))
	
	return start,end
	
def make_json(raw_messages):
	messages = []
	for m in raw_messages:
		messages.append(message_to_object(m))
	return json.dumps(messages,indent=4)
	
def make_xlsx(raw_messages):
	report = Report(header=('Date','Phone Number','Contact','Text'),rows=raw_messages.get_rows())
	return report.virtual()

def message_to_object(message):
	
	try:
		if message.connection.dhis2.facility:
			facility = {
				'name':unicode(message.connection.dhis2.facility),
				'id':message.connection.dhis2.facility.dhis2_id,
			}
		else:
			facility = None
	except (ObjectDoesNotExist):
		facility = None
		
	return {
		'phone_number':message.connection.identity,
		'facility':facility,
		'parsed':message.report_set.all().order_by('-pk')[0].commands,
		'text':message.text,
		'created':message.created.strftime("%Y-%m-%d %H:%M:%S")
	}

#TODO: There's probably a django utility to do this
def parse_date(date_str):
	return datetime.datetime.strptime(date_str,'%y-%m-%d')
