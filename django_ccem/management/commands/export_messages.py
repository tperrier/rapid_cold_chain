from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist

from dhis2 import models as dhis2
from django_ccem import models as ccem

import json
import code

class Command(BaseCommand):
	
	help = 'export all messages to json'
	
	def handle(self,*args,**kwargs):
	
		raw_messages = ccem.Message.objects.filter(is_submission=True,has_error=False)
		messages = []
		
		for m in raw_messages:
			messages.append(self.message_to_object(m))
			
		self.stdout.write(json.dumps(messages,indent=4))
		
		
	def message_to_object(self,message):
		
		try:
			facility = {
				'name':unicode(message.connection.dhis2.contact.facility),
				'id':message.connection.dhis2.contact.facility.dhis2_id,
			}
		except ObjectDoesNotExist:
			facility = None
			
		
		return {
			'phone_number':message.connection.identity,
			'facility':facility,
			'parsed':message.report_set.all().order_by('-pk')[0].commands,
			'text':message.text,
			'created':message.created.strftime("%Y-%m-%d %H:%M:%S")
		}
