#Create your admin definitions here
from django.contrib import admin
from models import *

class EnvayaOutgoingAdmin(admin.ModelAdmin):
	date_hierarchy = 'created'
	list_display = ('created','number','content','sent')
	
admin.site.register(EnvayaOutgoing,EnvayaOutgoingAdmin)
