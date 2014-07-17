#!/usr/bin/python
'''
Delete all objects from common tables
'''
import sys

# Setup Django Environment
sys.path.append('../') #path to rapid_cold_chain
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
