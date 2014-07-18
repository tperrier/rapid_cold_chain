#!/usr/bin/python
'''
Delete all objects from common tables
'''
import sys,os

# Setup Django Environment
PROJECT_ROOT = os.path.join(os.path.dirname(__file__),'..')
sys.path.append(PROJECT_ROOT) #path to rapid_cold_chain
from django.core.management import setup_environ
from rapid_sms import settings
setup_environ(settings)
# End Django Setup 

def _help():
	print 'No option found'


if len(sys.argv) == 1:
	_help()
	exit()

if sys.argv[1] == 'wipe':

	def delete(obj):
		if obj.objects.count() > 0:
			obj.objects.all().delete()
	
	import messagelog.models as log
	delete(log.Message)

	import django_ccem.models as ccem
	delete(ccem.Message)
	delete(ccem.Report)

	import rapidsms.models as rapid
	delete(rapid.Connection)

	import dhis2.models as dhis2
	delete(dhis2.OrganisationUnit)
	delete(dhis2.Facility)
	delete(dhis2.Contact)
	delete(dhis2.ContactConnection)

else:
	
	def count(obj):
		print obj,obj.objects.all().count()
	
	import django_ccem.models as ccem
	count(ccem.Message)
	count(ccem.Report)
	
	import dhis2.models as dhis2
	count(dhis2.OrganisationUnit)
	count(dhis2.Facility)
	count(dhis2.Contact)
	count(dhis2.ContactConnection)
	
	import rapidsms.models as rapid
	count(rapid.Connection)
	
	import messagelog.models as log
	count(log.Message)
