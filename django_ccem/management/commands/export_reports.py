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

    help = 'Export messages and reports as JSON'

    option_list = BaseCommand.option_list + (
        make_option ('-s','--start',help='Start date for message export yy-mm-dd'),
        make_option ('-e','--end',help='End date for message export yy-mm-dd'),
        make_option ('-c','--count',action='store_true',default=False,help='Display message count'),
        make_option ('-a','--all',action='store_true',default=False,help='Export ALL messages not only valid reports'),
        make_option ('-i','--no-indent',action='store_true',default=False,help='No indent for output'),
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

        raw_messages = ccem.Message.objects.filter(created__range=(start,end))
        if not kwargs['all']:
            raw_messages = raw_messages.filter(is_submission=True,has_error=False)

        messages = []

        if kwargs['count']:
            self.stdout.write('Messages: %i'%raw_messages.count())
            return

        for m in raw_messages:
            messages.append(message_to_object(m))
        if kwargs['no_indent']:
            self.stdout.write(json.dumps(messages))
        else:
            self.stdout.write(json.dumps(messages,indent=4))

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
	facility = None
    try:
		if message.connection.dhis2.facility:
			facility = {
				'name':unicode(message.connection.dhis2.facility),
				'id':message.connection.dhis2.facility.dhis2_id,
			}
	except (ObjectDoesNotExist):
		pass

    try:
        parsed = message.report_set.all().order_by('-pk')[0].commands
    except IndexError as e:
        parsed = None

    return {
        'phone_number':message.connection.identity,
        'facility':facility,
        'parsed':parsed,
        'text':message.text,
        'created':message.created.strftime("%Y-%m-%d %H:%M:%S")
    }

def parse_date(date_str):
    return datetime.datetime.strptime(date_str,'%y-%m-%d')
