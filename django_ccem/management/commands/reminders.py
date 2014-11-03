from optparse import make_option

from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist

from dhis2 import models as dhis2

#rapidsms imports
from rapidsms.router import send

import code,datetime

'''
Class to send reminders to facilities 

'''

class Command(BaseCommand):
	
	help = 'send remindes to facilities and managers'
	
	option_list = BaseCommand.option_list + (
		make_option ('-s','--send',help='send messages',action='store_true',default=False),
	)
	
	
	def handle(self,*args,**kwargs):
		self.options = kwargs
		self.monthly_reminders()
		
	
	def monthly_reminders(self):
		
		message = 'Khor khuam teau. Jark NIP:\nGa lou nar song SMS laiy ngarn pa jum deaun phajik 2014 garn jang teaun oun ha phoum luam therng'
		
		#get all connections to send to
		contacts = dhis2.Contact.objects.filter(facility__isnull=False)
		connections = []
		for contact in contacts:
			conn_set = contact.connection_set.filter(connection__backend__name='envaya')
			if len(conn_set) > 0:
				connections.append(conn_set[0].connection)
		
		self.stdout.write("Sending: %s"%self.options['send'])
		self.stdout.write("Messages to Send: %i"%len(connections))
		for i,conn in enumerate(connections):
			self.stdout.write('   %i: %s'%(i+1,conn))
			if self.options['send']:
				send(message,conn)
