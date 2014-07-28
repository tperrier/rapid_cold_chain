from django.db import models
from jsonfield import JSONField
import util.models as util, ccem_parser.parser.utils as utils

# Create your models here.

class Message(util.TimeStampedModel):
	'''
	A message model that acts like rapidsms.messagelog.message
	'''
	
	INCOMING,OUTGOING = 'I','O'
	DIRECTION_CHOICES = ((INCOMING,'Incoming'),(OUTGOING,'Outgoing'))
	
	#The raw text of the message
	text = models.CharField(max_length=200)
	
	#The connection that sent this message
	connection = models.ForeignKey('rapidsms.Connection',null=True,related_name='messages')
	
	#Direction of the message
	direction = models.CharField(max_length=1,choices=DIRECTION_CHOICES)
	
	#Boolean field if this messages looks like a submission
	is_submission = models.BooleanField(default=True)
	
	#Boolean field if last report message has an error
	has_error = models.BooleanField(default=False)
	
	class Meta:
		ordering = ('-created',)
	
	def save(self,*args,**kwargs):
		if self.direction == self.OUTGOING and self.is_submission:
			self.is_submission = False
		super(Message,self).save(*args,**kwargs)
	
	def __unicode__(self):
		return '#%i %s (%s)'%(self.id,self.created_str(),self.text)
	
	@property
	def num_reports(self):
		return self.report_set.count()

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
	error = models.CharField(max_length=50,null=True,blank=True)
	
	#Boolean indicating the presence of errors 
	has_error = models.BooleanField(default=False)
	
	#The cleaned version of the message text used to parse the data
	cleaned = models.CharField(max_length=200,null=True,blank=True)
	
	#Foreignkey link to Message that generated this report
	#A message may have multiple reports so create a OneToManyField (Foreign Key)
	message = models.ForeignKey(Message)
	#Foreignkey link to outgoing message response. Can only be one.
	response = models.OneToOneField(Message,null=True,blank=True,related_name='response_to')
	
	def save(self,*args,**kwargs):
		#Set the error status on the associated message object 
		if self.has_error and not self.message.has_error:
			self.message.has_error = True
			self.message.save()
		elif not self.has_error and self.message.has_error:
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
			error='%s: %s'%(msg.ccem_error.__class__.__name__,msg.ccem_error) if msg.ccem_error else None,
			message=msg.ccem_msg,
			cleaned=msg.ccem_parsed.cleaned,
			has_error=has_error
		)
	
	@classmethod
	def add_latest_response(cls,response):
		'''
		Given a rapidsms outgoing object attaches it to the correct report object if there is one
		'''
		#report = response.in_response_to.logger_msg.message.report_set.latest('created')
		#report.response = response.logger_msg
		if response.in_response_to.ccem_msg.report_set.count() > 0:
			report = response.in_response_to.ccem_msg.report_set.latest('created')
			report.response = response.ccem_msg
			report.save()
		
