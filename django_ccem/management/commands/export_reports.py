import datetime
from optparse import make_option

from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist

from dhis2 import models as dhis2
from django_ccem import models as ccem

import json
import code

class Command(BaseCommand):
	
	help = 'export all messages to json'
	
	option_list = BaseCommand.option_list + (
		make_option ('-s','--start',help='Start date for message export yy-mm-dd'),
		make_option ('-e','--end',help='End date for message export yy-mm-dd'),
		make_option ('-c','--count',action='store_true',default=False,help='Display message count'),
	)
	
	def handle(self,*args,**kwargs):
		
		start = datetime.date(2013,7,1)
		if kwargs['start']:
			start = parse_date(kwargs['start'])
			
		end = datetime.date.today()
		if kwargs['end']:
			end = parse_date(kwargs['end'])
			
		start = datetime.datetime.combine(start,datetime.time())
		end = datetime.datetime.combine(end,datetime.time())
	
		raw_messages = ccem.Message.objects.filter(is_submission=True,has_error=False,created__range=(start,end))
		messages = []
		
		if kwargs['count']:
			self.stdout.write('Messages: %i'%raw_messages.count())
			return
		
		for m in raw_messages:
			messages.append(message_to_object(m))
			
		self.stdout.write(json.dumps(messages,indent=4))
		
'''
Utility Functions
'''
def message_to_object(message):
	
	try:
		facility = {
			'name':unicode(message.connection.dhis2.contact.facility),
			'id':message.connection.dhis2.contact.facility.dhis2_id,
		}
	except (ObjectDoesNotExist,AttributeError):
		facility = None
		
	
	return {
		'phone_number':message.connection.identity,
		'facility':facility,
		'parsed':message.report_set.all().order_by('-pk')[0].commands,
		'text':message.text,
		'created':message.created.strftime("%Y-%m-%d %H:%M:%S")
	}
	
def parse_date(date_str):
	return datetime.datetime.strptime(date_str,'%y-%m-%d')
