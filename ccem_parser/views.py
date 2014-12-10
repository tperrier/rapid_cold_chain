# Create your views here.

from django.shortcuts import render, render_to_response

import parser

def test_message(request):
	message,parsed,error = request.GET.get('message',None),None,None
	if message:
		parsed,error = parser.parse(message)
		
	return render_to_response('test_message.html',{'message':message,'parsed':repr(parsed),'error':str(error)})
