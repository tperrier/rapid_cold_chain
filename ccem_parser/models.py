from django.db import models

# Create your models here.

class MessageResponse(models.Model):
	
	#keyword to lookup message by
	keyword = models.CharField(max_length=50)
	
	#Two letter language Code i.g: en,ke,lo
	language = models.CharField(max_length=5)
	
	message = models.CharField(max_length=200)
	
