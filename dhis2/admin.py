#Create your admin definitions here
from django.contrib import admin
from util.admin import RelatedFieldAdmin
from models import *


class FacilityAdmin(admin.ModelAdmin):
	pass
	
admin.site.register(Facility,FacilityAdmin)
admin.site.register(OrganisationUnit,FacilityAdmin)
	

