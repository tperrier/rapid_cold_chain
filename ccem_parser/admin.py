#Create your admin definitions here
from django.contrib import admin

from models import *

class StoredMessageAdmin(admin.ModelAdmin):
	
	list_display = ('keyword','language','message')
	
admin.site.register(StoredMessage,StoredMessageAdmin)
