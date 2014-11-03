import logging

from django.forms import widgets
from django import forms


#rapidsms imports
from rapidsms.backends.http.forms import BaseHttpForm

logger = logging.getLogger(__name__)

class EnvayaReceiveForm(forms.Form):
	
	
	phone_number = forms.CharField(initial="1111-test")
	action = forms.CharField(initial="incoming")
	#now = forms.DateTimeField(initial="1390433250705",input_formats=["%U%u"])
	now = forms.CharField(initial="1390433250705")
	
	log = forms.CharField(widget=widgets.Textarea,required=False)
	power = forms.IntegerField(initial="0")
	battery = forms.IntegerField(initial="0")
	network = forms.CharField(initial="WIFI")
	
	#message options
	
	message_type = forms.CharField(required=False,initial="sms")
	message = forms.CharField(required=False,initial="Test message")
	#timestamp = forms.DateTimeField(initial="1390433248000",input_formats=["%U%u"])
	timestamp = forms.CharField(initial="1390433248000")
	
	def __init__(self,*args,**kwargs):
		super(EnvayaReceiveForm,self).__init__(*args,**kwargs)
		self.fields['from'] = forms.CharField(initial="1234")
		
	
class EnvayaSendForm(forms.Form):
	phone_number = forms.CharField(max_length=15,initial='1234')
	message = forms.CharField(widget=widgets.Textarea)
		
	
