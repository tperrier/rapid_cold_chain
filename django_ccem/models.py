from django.db import models
from jsonfield import JSONField

# Create your models here.

class TimeStampedModel(models.Model):
	
	#The date and time this message was created or modified
	created = models.DateTimeField(auto_now_add=True)
	modified = models.DateTimeField(auto_now=True)
	
	class Meta:
		abstract = True

class Message(TimeStampedModel):
	'''
	A message model that links to the RapidSMS messagelog message
	'''
	
	#The RapidSMS log message this message is based on.
	message = models.ForeignKey('messagelog.Message')
	
	#The cleaned version of the message text used to parse the data
	cleaned = models.CharField(max_length=200)
	
	#Boolean field if this messages looks like a submission
	is_submission = models.BooleanField(default=True)

class SubmissionMessageManager(models.Manager):
	
	def get_queryset(self):
		return super(SubmissionMessageManager,self).get_queryset().filter(is_submission=True)
		
class RegularMessageManager(models.Manager):
	
	def get_queryset(self):
		return super(RegularMessageManager,self).get_queryset().filter(is_submission=False)

class SubmissionMessage(Message):
	'''
	A proxy model for Message that has a special Manager filtering on is_submission = True
	'''
	
	objects = SubmissionMessageManager()
	
	class Meta:
		proxy = True #make this a proxy model 
		
class RegularMessage(Message):
	'''
	A proxy model for Message that has a special Manager filtering on is_submission = False
	'''
	
	objects = RegularMessageManager()
	
	def save(self,*args,**kwargs):
		self.is_submission = False
		super(RegularMessage,self).save(*args,**kwargs)
	
	class Meta:
		proxy = True #make this a proxy model
	
class Report(TimeStampedModel):
	'''
	A parsed message report linking back to the originial message
	'''
	
	#JSON serialized Python objects for the parsed commands and errors
	commands = JSONField()
	errors = JSONField()
	
	#Boolean indicating the presence of errors 
	has_error = models.BooleanField(default=False)
	
	#Forignkey link to Message that generated this report and response
	message = models.ForeignKey(Message)
	response = models.ForeignKey('messagelog.Message',null=True,blank=True)
	
class DHIS2Object(models.Model):
	
	dhis2_id = models.CharField(max_length=20) #possibly make this the primary key
	
	class Meta:
		abstract = True

class OrganisationBase(DHIS2Object,TimeStampedModel):
	"""
	Abstract class definition for element in the Organisational Hierarchy
	"""
	
	'''
	A Json object representing the OrganisationUnits name in multiple languages
	formate {
		'ke':
		'lo':
	}
	'''
	i18n_name = JSONField()
	
	dhis2_code = models.CharField(max_length=20)
	
	level = models.IntegerField() 
	
	class Meta:
		abstract = True
		
	def __unicode__(self):
		return '|'.join([' '+i+' ' for i in self.i18n_name.values()])
	
class OrganisationUnit(OrganisationBase):
	"""
	An organizational unit in the hierarchy that is not a facility 
	"""
	#The parent of this entity in the hierarchy.  If blank, indicates a root node
	parent = models.ForeignKey('self',blank=True,null=True,related_name='children')
	
	#API Name for access to DHIS2
	dhis2_api_name = 'organisationUnits'
	
	
class Facility(OrganisationBase):
	
	#The parent hierarchy related Manager is OrganisationUnit.facility_set.all()
	parent = models.ForeignKey(OrganisationUnit,blank=True,null=True) 
	
	dhis2_api_name = 'organisationUnits'
	
class Equitment(DHIS2Object,TimeStampedModel):
	
	facility = models.ForeignKey(Facility,blank=True,null=True)
	
	equitment_type = models.CharField(max_length=50)
	
	working = models.BooleanField(default=True)
	
	dhis2_api_name = 'equipments'
