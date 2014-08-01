from django.core.management.base import BaseCommand, CommandError
		
class Command(BaseCommand):
	
	help = 'Wipe all data from database'
	
	def handle(self,*args,**kwargs):
		
		try:
			import rapidsms.backends.database.models as backend
			self.delete(backend.BackendMessage)
		except Exception as e:
			print e
			self.stdout.write('Import Error: backend')

		try:
			import django_ccem.models as ccem
			self.delete(ccem.Message)
			self.delete(ccem.Report)
		except:
			self.stdout.write('Import Error: django_ccem')
			
		try:
			import rapidsms.models as rapid
			self.delete(rapid.Connection)
		except:
			self.stdout.write('Import Error: rapidsms')
			
		try:
			import dhis2.models as dhis2
			self.delete(dhis2.OrganisationUnit)
			self.delete(dhis2.Facility)
			self.delete(dhis2.Contact)
			self.delete(dhis2.ContactConnection)
		except:
			self.stdout.write('Import Error: dhis2')
	
	def delete(self,obj):
		objs = obj.objects.all()
		count = objs.count()
		self.stdout.write('Deleting %i objects from %s'%(count,obj.__name__))
		while obj.objects.all().count() > 0:
			objs = [i[0] for i in obj.objects.all().values_list('pk')[:25]]
			obj.objects.filter(pk__in=list(objs)).delete()
