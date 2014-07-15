from django.db import models

# Create your models here.

class StoredMessage(models.Model):
	
	#keyword to lookup message by
	keyword = models.CharField(max_length=50)
	
	#Two letter language Code i.g: en,ke,lo
	language = models.CharField(max_length=5)
	
	message = models.CharField(max_length=200)
	
	
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
