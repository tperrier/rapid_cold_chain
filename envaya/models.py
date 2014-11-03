from django.db import models
import util.models as util
from response import EnvayaResponse
	
class EnvayaOutgoingManager(models.Manager):
	
	def outgoing(self):
		return self.filter(sent=False)
	
	def response(self,send=False):
		response = EnvayaResponse()
		for message in self.outgoing():
			response.add(message=message.content,to=message.number,id=message.message_id)
		if send:
			self.mark_sent()
		return response
		
	def mark_sent(self):
		return self.outgoing().update(sent=True)
	
class EnvayaOutgoing(util.TimeStampedModel):
	
	objects = EnvayaOutgoingManager()
	
	number = models.CharField(max_length=15)
	content = models.TextField()
	message_id = models.CharField(max_length=64,blank=True)
	sent = models.BooleanField(default=False)
	
	def mark_sent(self):
		self.sent = True
		self.save()
	
