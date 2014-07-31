from django.core.management.base import BaseCommand, CommandError
		
class Command(BaseCommand):
	
	help = 'Displays counts for all models'
	
	def handle(self,*args,**options):
		
		import django_ccem.models as ccem
		self._count(ccem.Message)
		self._count(ccem.Report)
		
		import dhis2.models as dhis2
		self._count(dhis2.OrganisationUnit)
		self._count(dhis2.Facility)
		self._count(dhis2.Contact)
		self._count(dhis2.ContactConnection)
		
		import rapidsms.models as rapid
		self._count(rapid.Connection)
		
		import rapidsms.backends.database.models as backend
		self._count(backend.BackendMessage)
		
	def _count(self,obj):
		self.stdout.write('%s: %i'%(obj.__name__,obj.objects.all().count()))
