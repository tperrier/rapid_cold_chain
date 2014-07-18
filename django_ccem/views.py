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
	contact = request.GET.get('contact',None)
	if contact is not None:
		contact="+"+contact.strip() if contact.startswith(' ') else contact
		message_list=message_list.filter(message__connection__identity=contact)
	order = request.GET.get('order',None)
	if order is not None:
		if order=='date': order='created'
		elif order=='contact': order='message__connection__identity'
		message_list=message_list.order_by(order);
	return message_render(request,message_list)

def message_render(request,message_list):
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

	return render(request,'messages.html',{'messages':messages})
