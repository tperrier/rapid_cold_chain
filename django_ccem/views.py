# Create your views here.
from django.shortcuts import render
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger

import models as ccem

def base_view(request):
	return render(request, 'ccem_sim/base.html')
	
def custom_view(request):
	return render(request, 'custom.html')
	
def messages(request,filter=None):
	
	message_list = ccem.Message.objects.all()
	if filter:
		message_list=message_list.filter(is_submission=True if filter=="submission" else False)
	paginator = Paginator(message_list,10)
	
	page = request.GET.get('page',1)
	try:
		messages = paginator.page(page)
	except PageNotAnInteger:
		# If page is not an integer, deliver first page.
		messages = paginator.page(1)
	except EmptyPage:
		# If page is out of range (e.g. 9999), deliver last page of results.
		messages = paginator.page(paginator.num_pages)

	print dir(messages[0].from_msg)
	return render(request,'messages.html',{'messages':messages})
