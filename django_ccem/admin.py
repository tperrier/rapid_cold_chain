# Create your views here.
from django.contrib import admin
from util.admin import RelatedFieldAdmin
from models import *

class MessageAdmin(RelatedFieldAdmin):
	
	list_display = ('message__date','message__text','message__connection')
	
class FacilityAdmin(admin.ModelAdmin):
	pass


admin.site.register(SubmissionMessage,MessageAdmin)
admin.site.register(RegularMessage,MessageAdmin)
admin.site.register(OrganisationUnit,FacilityAdmin)
admin.site.register(Facility,FacilityAdmin)

	

