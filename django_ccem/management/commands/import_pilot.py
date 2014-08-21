from django.core.management.base import BaseCommand, CommandError

from dhis2 import api
from dhis2 import models as dhis2

import code

class Command(BaseCommand):
	
	help = 'import all new pilot sites'
	
	def handle(self,*args,**kwargs):
	
		piolt_sites = api.get_from_id('organisationUnitGroups','NVIkyUs4s0s',json=True)['organisationUnits']
		
		print "Found %i Piolt Sites"%len(piolt_sites)
		
		for site in piolt_sites:
			dhis2.OrganisationUnit.create_if_not_exists(site['id'],follow_up=True)
