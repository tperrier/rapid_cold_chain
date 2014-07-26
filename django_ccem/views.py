# Create your views here.
import datetime,json

from django.shortcuts import render
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger

import models as ccem, dhis2.models as dhis2,rapidsms.models as rapid

def base_view(request):
	return render(request, 'ccem_sim/base.html')

def contacts(request):
	
	#All Connections
	connection_list = rapid.Connection.objects.all()
	
	#contact details
	contact_detail, contact_message_list = None, None
	contact = _get_contact(request)
	if contact is not None:
		contact_conn = dhis2.ContactConnection.objects.filter(connection__identity=contact)
		#contact_conn = rapid.Connection.objects.filter(identity=contact)
		contact_message_list = ccem.Message.objects.filter(connection__identity=contact)
		if contact_conn.count()>0:
			contact_detail = contact_conn[0].contact
	
	return render(request, 'contacts.html',{'contacts':connection_list,'contact_detail':contact_detail,'messages':contact_message_list})

def facility_list(request):
	facility_list = dhis2.Facility.objects.all()
	if facility_list.count()>0:
		org = facility_list[0]
		levels = facility_list[0].level
		for i in range(0,(levels-1)): org = org.parent
	return render(request, 'facility_list.html', {'facility_list':org, 'root_id': org.dhis2_id });

def facilities(request):
	facility_list = dhis2.Facility.objects.all()
	if facility_list.count()>0:
		org = facility_list[0]
		levels = facility_list[0].level
		for i in range(0,(levels-1)): org = org.parent
	facility_id = request.GET.get('id',None)
	facility = None
	print facility_id
	if facility_id is not None:
		facility = dhis2.Facility.objects.all().filter(dhis2_id=facility_id).get()
		print facility.dhis2_id
	#root_org = {'wbZtszn1b0R':{'name':{'ke':'Lao PDR'},'children':['FRmrFTE63D0']},'FRmrFTE63D0': {'name':{'lo': u'\u0e9a\u0ecd\u0ec8\u0ec1\u0e81\u0ec9\u0ea7', 'ke': 'Bokeo'}}}
	#json.dumps(root_orgs)
	return render(request, 'facilities.html', {'facility_list':org,'facility': facility, 'root_id': org.dhis2_id })
	
def messages(request):
		
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

