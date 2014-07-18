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


import messagelog.models as log
log.Message.objects.all().delete()

import django_ccem.models as ccem
ccem.Message.objects.all().delete()
ccem.Report.objects.all().delete()

import rapidsms.models as rapid 
rapid.Connection.objects.all().delete()
rapid.Contact.objects.all().delete()

import dhis2.models as dhis2
dhis2.OrganisationUnit.objects.all().delete()
dhis2.Facility.objects.all().delete()
