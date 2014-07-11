from django.db import models
from jsonfield import JSONField
import util.models as util

# Create your models here.

class Message(util.TimeStampedModel):
	'''
	A message model that links to the RapidSMS messagelog message
	'''
	
	#The RapidSMS log message this message is based on.
	#There can only be one incoming message that created this Message
	message = models.OneToOneField('messagelog.Message')
	
	#The cleaned version of the message text used to parse the data
	cleaned = models.CharField(max_length=200)
	
	#Boolean field if this messages looks like a submission
	is_submission = models.BooleanField(default=True)
	
	@classmethod
	def from_msg(cls,msg,parsed):
		'''
		Create a new message from a rapidsms msg object and parser result
		'''
		submission = False if 'NO_KEYWORD_FOUND' in parsed.errors else True #ERROR_CODE
		return cls.objects.create(message=msg.logger_msg,cleaned=parsed.cleaned,is_submission=submission)

class SubmissionMessageManager(models.Manager):
	
	def get_query_set(self):
		return super(SubmissionMessageManager,self).get_query_set().filter(is_submission=True)
		
class RegularMessageManager(models.Manager):
	
	def get_query_set(self):
		return super(RegularMessageManager,self).get_query_set().filter(is_submission=False)

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
	
class Report(util.TimeStampedModel):
	'''
	A parsed message report linking back to the originial message
	'''
	
	#JSON serialized Python objects for the parsed commands and errors
	commands = JSONField()
	errors = JSONField()
	
	#Boolean indicating the presence of errors 
	has_error = models.BooleanField(default=False)
	
	#Foreignkey link to Message that generated this report
	#A message may have multiple reports so create a OneToManyField (Foreign Key)
	message = models.ForeignKey(Message)
	#Foreignkey link to outgoing message response. Can only be one.
	response = models.OneToOneField('messagelog.Message',null=True,blank=True)
	
	@classmethod
	def from_ccem(cls,msg,parsed):
		'''
		Create a new report from a CCEM message and parsed object
		'''
		
		has_error = False if len(parsed.errors)==0 else True
		
		return cls.objects.create(commands=parsed.commands,errors=parsed.errors,message=msg,has_error=has_error)
	
	@classmethod
	def add_latest_response(cls,response):
		'''
		Given a rapidsms outgoing object attaches it to the correct report object if there is one
		'''
		report = response.in_response_to.logger_msg.message.report_set.latest('created')
		report.response = response.logger_msg
		report.save()
		
## Move all this to a DHIS2 App
class DHIS2Object(models.Model):
	
	dhis2_id = models.CharField(max_length=20,primary_key=True) 
	
	class Meta:
		abstract = True

class OrganisationBase(DHIS2Object,util.TimeStampedModel):
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
	
class Equitment(DHIS2Object,util.TimeStampedModel):
	
	facility = models.ForeignKey(Facility,blank=True,null=True)
	
	equitment_type = models.CharField(max_length=50)
	
	working = models.BooleanField(default=True)
	
	dhis2_api_name = 'equipments'
