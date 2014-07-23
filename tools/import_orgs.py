#!/usr/bin/python
import json,datetime,sys,os,code

# Setup Django Environment
FILE_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.join(FILE_DIR,'..')
sys.path.append(PROJECT_ROOT) #path to rapid_cold_chain
from django.core.management import setup_environ
from rapid_sms import settings
setup_environ(settings)
# End Django Setup 

import dhis2.models as dhis2

dhis2.OrganisationUnit.create_if_not_exists('JkDRFRhTl7C',follow_up=True,follow_down=True)
