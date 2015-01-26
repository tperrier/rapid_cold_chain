#python imports
import logging, pprint, json, traceback,code

#django imports
from django.views.generic.edit import FormView
from django.views.generic.base import View

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotFound
from django.shortcuts import render, render_to_response

from django.utils import translation 

#rapidsms imports
from rapidsms.router import receive, lookup_connections, send

#envaya imports
from response import EnvayaResponse
import models, forms
from ccem_parser import parser
logger = logging.getLogger(__name__)

class EnvayaView(View):
	
	backend_name = 'envaya'
	http_method_names = ['post']
	
	@method_decorator(csrf_exempt)
	def dispatch(self, *args, **kwargs):
		"""
		Wraps the main entry point into the view with the csrf_exempt
		decorator, which most (if not all) clients using this view will not
		know about.
		"""
		#~ logger.debug("Dispatch: \n\tPOST:%s\n\tFrom: %s",args[0].POST,args[0].META['HTTP_USER_AGENT'])
		return super(EnvayaView, self).dispatch(*args, **kwargs)
		
	def post(self,request):
		action = request.POST.get('action',None)
		logger.debug('Action: %s'%action)
		if action:
			try:
				if action=="incoming":
					#only parse sms messages not calls or mms
					if request.POST.get('message_type',None)=='sms':
						return self.handle_message()
					else:
						return EnvayaHttpResponse(log='only sms messages supported',status=400)
				elif action=="device_status":
					return EnvayaHttpResponse('Status Recieved')
				elif action=="test":
					return EnvayaHttpResponse('Test Ok')
				elif action=='outgoing':
					return EnvayaOutgoingResponse()
				elif action=='send_status':
					return EnvayaHttpResponse(log='Confirm Sent')
				else:
					return EnvayaHttpResponse(log='action not implemented',status=404)
			except KeyError as e:
				logger.debug("Required POST value missing. "+str(e))
				return EnvayaHttpResponse(log="Required POST value missing. "+str(e),status=400)
		else:
			return EnvayaHttpResponse(log='action required',status=400)
	
	def get_model_kwargs(self,*extra_values): #throws KeyError
		#add extra values to base values
		event_values = ['phone_number','network','now','battery','power']
		event_values.extend(extra_values)
		#make kwarg dict of event name and request post value
		return {value:self.request.POST[value] for value in event_values}
		
	def handle_message(self):
		event_kwargs = self.get_model_kwargs('from','message','timestamp')
		#fix variables for model 
		event_kwargs['sender'] = event_kwargs.pop('from')
		connection = lookup_connections('envaya', [event_kwargs['sender']])[0]
		msg_in = receive(event_kwargs['message'],connection)		
		return EnvayaOutgoingResponse()

		
class ReceiveView(FormView):
	'''
	Test Envaya Receive 
	'''
	form_class = forms.EnvayaReceiveForm
	template_name = "envaya_test.html"
	backend_name = None
		
	def form_valid(self, form):
		if self.request.method == 'GET':
			self.request.POST = self.request.GET.copy()
		return EnvayaView.as_view(backend_name="envaya")(self.request)
		return HttpResponse("<pre>%s</pre>"%(pprint.pformat(form.cleaned_data),))
		
class SendView(FormView):
	
	form_class = forms.EnvayaSendForm
	template_name = 'envaya_test.html'
	
	def form_valid(self,form):
		connection = lookup_connections('envaya',[form.cleaned_data['phone_number']])[0],
		text = form.cleaned_data['message']
		
		send(text,connection)
		
		return HttpResponse("<pre>%s</pre>"%(pprint.pformat(form.cleaned_data),))

@csrf_exempt
def training_view(request):
	if request.method == 'GET':
		return render(request,'envaya_training.html')
	elif request.method == 'POST':
		action = request.POST.get('action',None)
		if action:
			try:
				if action=="incoming": #only parse sms messages not calls or mms
					
					if request.POST.get('message_type',None)=='sms':
						#Get parsed message response 
						ccem_parsed,ccem_error = parser.parse(request.POST['message'])
						
						#Switch Language To Lao Karaoke
						translation.activate('ka') 
						message = unicode(ccem_parsed) if not ccem_error else unicode(ccem_error)
						models.EnvayaTraining.objects.create(
							**{'number':request.POST['from'],'content':request.POST['message'],'response':message}
						)
						if request.POST.get('http_test',False): #Comming from the HTTP Test Form
							return render(request,'envaya_training.html',{'response':message})
						else: #Comming from Envaya
							response = EnvayaResponse(messages=[{'message':message,'to':request.POST['from']}])
							return EnvayaHttpResponse(response=response)
					else:
						return EnvayaHttpResponse(log='only sms messages supported',status=400)
				elif action=="device_status":
					return EnvayaHttpResponse('Status Recieved')
				elif action=="test":
					print "test"
					return EnvayaHttpResponse('Test Ok')
				elif action=='outgoing':
					return EnvayaOutgoingResponse()
				elif action=='send_status':
					return EnvayaHttpResponse(log='Confirm Sent')
				else:
					return EnvayaHttpResponse(log='action not implemented',status=404)
			except KeyError as e:
				return EnvayaHttpResponse(log="Required POST value missing. "+str(e),status=400)
		else:
			return EnvayaHttpResponse(log='action required',status=400)
	


def EnvayaOutgoingResponse():
	response = models.EnvayaOutgoing.objects.response(send=True)
	message_count = len(response)
	if message_count > 0:
		log = 'Messages To Send: %i'%len(response)
		response.log(log)
	return EnvayaHttpResponse(response=response)

def EnvayaHttpResponse(log=None,response=None,status=200):
	if isinstance(response,EnvayaResponse):
		if not response.has_log() and log:
			response.log(log)
		return JsonHttpResponse(response.to_json(),status)
	return JsonHttpResponse(EnvayaResponse(log=log).to_json(),status)
	
def JsonHttpResponse(json_str,status=200):
	return HttpResponse(json_str,content_type='application/json',status=status)
