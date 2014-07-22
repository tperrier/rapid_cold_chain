from django.db import models
import utils

# Create your models here.

class StoredMessageManager(models.Manager):
	
	language = 'en'
	
	def get_from_error(self,error):
		messages = super(StoredMessageManager,self).get_query_set().filter(keyword=error.keyword)
		if messages.count() > 0:
			return messages
		messages = super(StoredMessageManager,self).get_query_set().filter(keyword=utils.DEFAULT_KEYWORD)
		if messages.count() > 0:
			return messages
		return error.getMessage(language)

class StoredMessage(models.Model):
	
	#keyword to lookup message by
	keyword = models.CharField(max_length=50)
	
	#Two letter language Code i.g: en,ke,lo
	language = models.CharField(max_length=5)
	
	message = models.CharField(max_length=200)
	
	
	objects = StoredMessageManager()
	
	@classmethod
	def get_from_keyword(cls,keyword,language='en',**kwargs):
		keyword_msgs = cls.objects.filter(keyword=keyword)
		
		language_msgs = keyword_msgs.filter(language=language)
		
		if language_msgs.count() > 0:
			return language_msgs[0].message.format(**kwargs)
		elif keyword_msgs.count() > 0:
			return keyword_msgs[0].message.format(**kwargs)
		else:
			return keyword
			

