# Create your views here.
from django.contrib import admin
from util.admin import RelatedFieldAdmin
from models import *

class MessageAdmin(RelatedFieldAdmin):
	
	list_display = ('created','message__text','message__connection')
	
class FacilityAdmin(admin.ModelAdmin):
	pass
	
class ReportAdmin(RelatedFieldAdmin):
	
	list_display = ('created','commands','errors')


admin.site.register(SubmissionMessage,MessageAdmin)
admin.site.register(RegularMessage,MessageAdmin)
admin.site.register(OrganisationUnit,FacilityAdmin)
admin.site.register(Facility,FacilityAdmin)
admin.site.register(Report,ReportAdmin)

	

