#Create your admin definitions here
from django.contrib import admin
from models import *

class EnvayaOutgoingAdmin(admin.ModelAdmin):
	date_hierarchy = 'created'
	list_display = ('created','number','content','sent')
	
class EnvayaTrainingAdmin(admin.ModelAdmin):
	date_hierarchy = 'created'
	list_display = ('created','number','content','response')
	
admin.site.register(EnvayaOutgoing,EnvayaOutgoingAdmin)
admin.site.register(EnvayaTraining,EnvayaTrainingAdmin)
