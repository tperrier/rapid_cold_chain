from optparse import make_option

from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist

#CCEM
from dhis2 import models as dhis2
from django_ccem import models as ccem

#rapidsms imports
from rapidsms.router import send

import code,datetime

'''
Class to send reminders to facilities 

'''

class Command(BaseCommand):
	
	help = 'send remindes to facilities and managers'
	
	action_list = ['monthly','missed','test']
	
	
	option_list = BaseCommand.option_list + (
		make_option('-s','--send',help='send messages',action='store_true',default=False),
		make_option('--silent',help='don\t print output',action='store_true',default=False),
		make_option('-a','--action',help='action to preform [%s]'%' '.join(action_list),choices=action_list,default='monthly')
	)
	
	
	def handle(self,*args,**kwargs):
		self.options = kwargs
		if kwargs['action'] == 'monthly':
			self.monthly_reminders()
		elif kwargs['action'] == 'missed':
			self.missed_reminders()
		elif kwargs['action'] == 'test':
			self.test()
		
	
	def monthly_reminders(self):
		'''
		Send a monthly visit reminder to all Contacts associated with a facility.
		'''
		
		message = 'Khor khuam teau. Jark NIP:\nGa lou nar song SMS laiy ngarn pa jum deaun phajik 2014 garn jang teaun oun ha phoum luam therng jum nuan vaccine t yung leau'
		
		#get all connections to send to
		contacts = dhis2.Contact.objects.filter(facility__isnull=False)
		connections = []
		for contact in contacts:
			conn_set = contact.connection_set.filter(connection__backend__name='envaya')
			if len(conn_set) > 0:
				connections.append(conn_set[0].connection)
				
		self.send_batch(message,connections)
				
	def missed_reminders(self):
		
		message = 'Khor khuam teau. Jark NIP:\nGa lou nar song SMS laiy ngarn pa jum deaun phajik 2014 garn jang teaun oun ha phoum luam therng jum nuan vaccine t yung leau'
		facilities = self.missed_facilities()
		
		connections = []
		for facility in facilities:
			self.write(facility)
			for contact in facility.contact_set.all():
				for conn in contact.connection_set.all():
					connections.append(conn.connection)
					self.write('   %s'%conn)
		
		self.send_batch(message,connections,verbose=False)
		
		
	def missed_facilities(self):
		'''
		Return list of facilities that haven't sent a report in this month
		'''
		valid_messages = ccem.Message.objects.filter(created__month=datetime.date.today().month,is_submission=True)
		
		#get list of valid facilities
		facilities = []
		for message in valid_messages:
			try:
				facilities.append(message.connection.dhis2.contact.facility.dhis2_id)
			except Exception as e:
				pass
				
		return dhis2.Facility.objects.exclude(dhis2_id__in=facilities)
		
	def send_batch(self,message,connections,verbose=True):
		'''
		Send a single message to a list of connections
		'''
		self.write("Sending: %s"%self.options['send'],verbose=verbose)
		self.write("Messages to Send: %i"%len(connections),verbose=verbose)
		for i,conn in enumerate(connections):
			self.write('   %i: %s'%(i+1,conn),verbose=verbose)
			if self.options['send']:
				send(message,conn)
				
	def write(self,*args,**kwargs):
		verbose = kwargs['verbose'] if 'verbose' in kwargs else True
		if not self.options['silent'] and verbose:
			self.stdout.write(*[str(a) for a in args])
			
	def test(self):
		self.write('Test')
		F = dhis2.Facility.objects.all()
		self.write('All: %i'%F.count())
			
		self.write('Reporting: %i'%dhis2.Facility.objects.reporting().count())
		
		self.write('Missed: %i'%dhis2.Facility.objects.non_reporting().count())
		
		code.interact(local=locals())
