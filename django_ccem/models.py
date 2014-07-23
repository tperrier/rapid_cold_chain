from django.db import models
from jsonfield import JSONField
import util.models as util, ccem_parser.parser.utils as utils

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
	
	#Boolean field if last report message has an error
	has_error = models.BooleanField(default=False)
	
	def __unicode__(self):
		return '#%i %s (%s)'%(self.id,self.created_str(),self.cleaned)
	
	@property
	def num_reports(self):
		return self.report_set.count()
	
	@classmethod
	def from_msg(cls,msg):
		'''
		Create a new message from a rapidsms msg object and parser result
		'''
		submission = False if isinstance(msg.ccem_error,utils.NoKeywordError) else True
		return cls.objects.create(message=msg.logger_msg,cleaned=msg.ccem_parsed.cleaned,is_submission=submission)

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
	
	def save(self,*args,**kwargs):
		#Set the error status on the associated message object 
		if self.has_error:
			self.message.has_error = True
			self.message.save()
		else:
			self.message.has_error = False
			self.message.save()
		super(Report,self).save(*args,**kwargs)
	
	@classmethod
	def from_msg(cls,msg):
		'''
		Create a new report from a CCEM message and parsed object
		'''
		has_error = True if msg.ccem_error else False
		
		return cls.objects.create(
			commands=msg.ccem_parsed.commands,
			errors=[str(msg.ccem_error)],
			message=msg.ccem,
			has_error=has_error
		)
	
	@classmethod
	def add_latest_response(cls,response):
		'''
		Given a rapidsms outgoing object attaches it to the correct report object if there is one
		'''
		report = response.in_response_to.logger_msg.message.report_set.latest('created')
		report.response = response.logger_msg
		report.save()
		
