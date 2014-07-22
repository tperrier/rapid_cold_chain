# Create your views here.
import datetime

from django.shortcuts import render
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger

import models as ccem, dhis2.models as dhis2,rapidsms.models as rapid

def base_view(request):
	return render(request, 'ccem_sim/base.html')

def contacts(request):
	contact_list = dhis2.Contact.objects.all()
	contact_detail, message_list = None, None
	contact = request.GET.get('contact',None)
	if contact is not None:
		contact="+"+contact.strip() if contact.startswith(' ') else contact
		contact_conn = dhis2.ContactConnection.objects.filter(connection__identity=contact)
		#contact_conn = rapid.Connection.objects.filter(identity=contact)
		if contact_conn.count()>0:
			contact_detail = contact_conn[0].contact
			message_list = ccem.Message.objects.filter(message__connection__identity=contact)
	
	return render(request, 'contacts.html',{'contacts':contact_list,'contact_detail':contact_detail,'messages':message_list})
	
def messages(request):
		
	message_list = ccem.Message.objects.all()
	
	#filter based on message type
	msg_type = request.GET.get('type',None)
	if msg_type == 'submission':
		message_list = message_list.filter(is_submission=True)
	elif msg_type == 'regular':
		message_list = message_list.filter(is_submission=False)
	elif msg_type == 'flagged':
		message_list = message_list.filter(has_error=True)
	
	#filter based on contact
	contact = request.GET.get('contact',None)
	if contact is not None:
		contact="+"+contact.strip() if contact.startswith(' ') else contact
		message_list = message_list.filter(message__connection__identity=contact)
	
	#filter based on date
	start = _strpdate(request.GET.get('start',''))
	end = _strpdate(request.GET.get('end',''))
	
	if start is not None:
		message_list = message_list.filter(created__gte=start)
	if end is not None:
		message_list = message_list.filter(created__lte=end)
	
	order = request.GET.get('order',None)
	if order is not None:
		if order == 'date': order='created'
		elif order == 'contact': order='message__connection__identity'
		message_list=message_list.order_by(order);
	
	return message_render(request,message_list)

def _strpdate(datestr,format='%d/%m/%y'):
	try:
		return datetime.datetime.strptime(datestr,format)
	except ValueError:
		return None

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
		print "Debug Empty Page:",messages.has_next()

	return render(request,'messages.html',{'messages':messages})
