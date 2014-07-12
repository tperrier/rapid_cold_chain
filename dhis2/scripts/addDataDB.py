import requests,json,code
import sys
sys.path.append('../../')
from django.core.management import setup_environ
from rapid_sms import settings
setup_environ(settings)

import django_ccem.models as ccem

o = ccem.OrganisationUnit(dhis2_id='1',dhis2_code='1',level='1',i18n_name={'en':'Facility Name 1'})

o.save()