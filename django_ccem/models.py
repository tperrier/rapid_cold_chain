import datetime

from django.db import models
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist

from jsonfield import JSONField

import util.models as util, ccem_parser.parser.utils as utils

class MessageQuerySet(models.QuerySet):
	
	def month(self):
		'''
		Return messages for 3 days before and 10 days after start of current month
		#TODO: add offset
		'''
		today = datetime.date.today()
		month = datetime.datetime(today.year,today.month,1)
		
		start = month - datetime.timedelta(days=3)
		end = month + datetime.timedelta(days=10)
		
		return self.filter(direction='I').range(start,end)
	
	def range(self,start,end):
		if isinstance(start,basestring):
			start = datetime.datetime.strptime(start,'%y-%m-%d')
		if isinstance(end,basestring):
			end = datetime.datetime.strptime(end,'%y-%m-%d')
		
		tz = timezone.get_default_timezone()
		if timezone.is_naive(start):
			start = timezone.make_aware(start,tz)
		if timezone.is_naive(end):
			end = timezone.make_aware(end,tz)
			
		return self.filter(created__range=(start,end))
		
	def get_rows(self):
		''' Return generator of rows for query set
			Columns: date,identity,contact,text
		'''
		
		class RowGen(object):
			
			def __init__(this):
				this.messages = iter(self.all())
				
			def __iter__(this):
				return this
				
			def next(this):
				msg = this.messages.next()
				date = msg.created.strftime('%m-%d %H:%M')
				number = msg.connection.identity
				try:
					contact = msg.connection.dhis2.name
					facility = msg.connection.dhis2.facility
				except ObjectDoesNotExist as e:
					contact = ''
					facility = ''
				return [facility,contact,number,date,msg.text,msg.is_submission,not msg.has_error]
				
			def header(this):
				return ['Facility','Contact','Phone Number','Date','Message','Submission','Valid']
		
		return RowGen()
		
	
	def connection_frequancy(self):
		'''
		Count messages sent per connection 
		#TODO: add facility and breakdown by date
		'''
		connections = {}
		for msg in self.all():
			try:
				connections[msg.connection.identity] += 1
			except KeyError as e:
				connections[msg.connection.identity] = 1
		return connections

class SubmissionMessageQuerySet(MessageQuerySet):
	
	def get_queryset(self):
		return super(SubmissionMessageQuerySet,self).get_queryset().filter(is_submission=True)
		
class RegularMessageQuerySet(MessageQuerySet):
	
	def get_queryset(self):
		return super(RegularMessageQuerySet,self).get_queryset().filter(is_submission=False)

class Message(util.TimeStampedModel):
	'''
	A message model that acts like rapidsms.messagelog.message
	'''
	
	objects = MessageQuerySet.as_manager()
	
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
	
	#Boolean field if the last report message was ignored
	ignored = models.BooleanField(default=False)
	
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
		#return the number of reports for this message
		return self.report_set.count()
		
	@property
	def flagged(self):
		#boolean if the message should be flagged or not
		return self.has_error and not self.ignored

class SubmissionMessage(Message):
	'''
	A proxy model for Message that has a special Manager filtering on is_submission = True
	'''
	
	objects = SubmissionMessageQuerySet.as_manager()
	
	class Meta:
		proxy = True #make this a proxy model 
		
class RegularMessage(Message):
	'''
	A proxy model for Message that has a special Manager filtering on is_submission = False
	'''
	
	objects = RegularMessageQuerySet.as_manager()
	
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
	#A message may have multiple reports: OneToManyField (Foreign Key)
	message = models.ForeignKey(Message)
	
	#Foreignkey link to outgoing message response. Can only be one.
	response = models.OneToOneField(Message,null=True,blank=True,related_name='response_to')
	
	#Foreignkey link to facility that sent this message
	facility = models.ForeignKey('dhis2.Facility',null=True,blank=True)
	
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
		try:
			if response.in_response_to and response.in_response_to.ccem_msg.report_set.count() > 0:
				report = response.in_response_to.ccem_msg.report_set.latest('created')
				report.response = response.ccem_msg
				report.save()
				return report
		except AttributeError as e:
			pass
