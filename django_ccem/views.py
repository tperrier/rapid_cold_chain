# Create your views here.
import datetime,json

from django.shortcuts import render
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
from django.utils.datastructures import MultiValueDictKeyError


import rapidsms.router as router

import models as ccem, dhis2.models as dhis2,rapidsms.models as rapid, ccem_parser.parser as parser, util

def base_view(request):
	return render(request, 'ccem_sim/base.html')

def contacts(request):
	
	#All Contacts
	contact_list = dhis2.Contact.objects.all()
	
	#All anonymous connections without a contact 
	anonymous_list = rapid.Connection.objects.filter(dhis2=None)
	
	#contact details
	contact_detail, contact_message_list = None, None
	contact = _get_contact(request)
	if contact is not None:
		contact_detail = util.get_or_none(dhis2.Contact,connection__identity=contact)
		if contact_detail is not None:
			connection = contact_detail.connection
		else:
			connection = util.get_or_none(rapid.Connection,identity=contact)
			
		contact_message_list = ccem.Message.objects.filter(connection__identity=contact)

		#POST: Submit Message
		if request.method == 'POST':
			message = request.POST['message']
			router.send(message,contact_detail.connection)	
	return render(request, 'contacts.html',{
		'contacts':contact_list,
		'anonymous':anonymous_list,
		'connection':connection,
		'contact':contact_detail,
		'messages':contact_message_list}
	)

def facilities(request):
	facility_id = request.GET.get('id',None)
	facility = util.get_or_none(dhis2.Facility,dhis2_id=facility_id)
	contacts = dhis2.Contact.objects.filter(facility=facility)
	return render(request, 'facilities.html', {'facility': facility,'contacts':contacts})
	
def messages(request):
	
	#POST: Reparse report
	if request.method == 'POST':
		
		message = ccem.Message.objects.get(id=request.POST['message'])
		
		try:
			request.POST['fix']
		except MultiValueDictKeyError: #Not a fix submission so ignore message
			message.has_error = False
			message.save()
		else: #Submit a fix report
			text = request.POST['text']
			parsed,error = parser.parse(text)
				
			report = ccem.Report.objects.create(
				commands = parsed.commands,
				error = '%s: %s'%(error.__class__.__name__,error) if error else None,
				message = message,
				cleaned = parsed.cleaned,
				has_error = True if error else False
			)
		
	
	message_list = ccem.Message.objects.all()
	
	#filter based on get params
	msg_type = request.GET.get('type',None)
	if msg_type == 'submission':
		message_list = message_list.filter(is_submission=True)
	elif msg_type == 'regular':
		message_list = message_list.filter(is_submission=False,direction=ccem.Message.INCOMING)
	elif msg_type == 'outgoing':
		message_list = message_list.filter(direction=ccem.Message.OUTGOING)
	elif msg_type == 'flagged':
		message_list = message_list.filter(has_error=True)
	
	#filter based on contact
	contact = _get_contact(request)
	if contact is not None:
		message_list = message_list.filter(message__connection__identity=contact)
	
	#filter based on date
	start = _strpdate_or_none(request.GET.get('start',''))
	end = _strpdate_or_none(request.GET.get('end',''))
	if start is not None:
		message_list = message_list.filter(created__gte=start)
	if end is not None:
		message_list = message_list.filter(created__lte=end)
	
	order = request.GET.get('order',None)
	if order is not None:
		if order == 'date': order='created'
		elif order == 'contact': order='message__connection__identity'
		message_list=message_list.order_by(order);
	#End message_list filtering
	
	#Make a paginator from message list 
	paginator = Paginator(message_list,10)
	
	page = request.GET.get('page',1)
	try:
		message_page = paginator.page(page)
	except PageNotAnInteger:
		# If page is not an integer, deliver first page.
		message_page = paginator.page(1)
	except EmptyPage:
		# If page is out of range (e.g. 9999), deliver last page of results.
		message_page = paginator.page(paginator.num_pages)

	return render(request,'messages.html',{'messages':message_page})

def _strpdate_or_none(datestr,format='%d/%m/%y'):
	'''
	Return a datetime objecet from a string or None
	'''
	try:
		return datetime.datetime.strptime(datestr,format)
	except ValueError:
		return None
		
def _get_contact(request):
	#gets contact from request if exists and adds + if need
	contact = request.GET.get('contact',None)
	if contact and contact.startswith(' '):
		contact = '+'+contact.strip()
	return contact

