# Create your views here.
import code

from django.shortcuts import render, render_to_response
from django.utils import translation

import parser

def test_message(request):
	message,parsed,error = request.GET.get('message',None),None,None
	if message:
		parsed,error = parser.parse(message)
	
	#~ code.interact(local=locals())
	return render_to_response('test_message.html',msg_dict(message,parsed,error))
	
def test_message_list(request):
	
	translation.activate('ka')
	
	valid,invalid = [],[]
	verbose = True if request.GET.get('verbose','Simple') =='Verbose' else False
	
	print verbose
	#test all valid messages
	for msg in parser.VALID_LIST:
		parsed,error = parser.parse(msg)
		valid.append(msg_dict(msg,parsed,error))
		
	#test all invalid messages
	for msg in parser.INVALID_LIST:
		parsed,error = parser.parse(msg)
		invalid.append(msg_dict(msg,parsed,error))
	
	return render_to_response('test_message_list.html',{'valid':valid,'invalid':invalid,'verbose':verbose})

def msg_dict(message,parsed,error):
	'''
	Convert a messsage into a dictionary for view context
	'''
	return {
		'message':message,
		'cleaned':parsed.cleaned if parsed else None,
		'parsed':repr(parsed),
		'error':str(error),
		'response':str(parsed)
	}
