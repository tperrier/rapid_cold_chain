#Create your admin definitions here
from django.contrib import admin
from util.admin import RelatedFieldAdmin
from models import *



class ReportInline(admin.TabularInline):
	model = Report
	fk_name = 'message'
	extra = 1

class MessageAdmin(RelatedFieldAdmin):
	
	list_display = ('created','text','connection','has_error','direction','num_reports')
	
	readonly_fields = ('created','modified')
	
	inlines = (ReportInline,)

class ReportAdmin(RelatedFieldAdmin):
	
	list_display = ('created','commands','error','has_error','facility')


admin.site.register(SubmissionMessage,MessageAdmin)
admin.site.register(RegularMessage,MessageAdmin)
admin.site.register(Report,ReportAdmin)

	

