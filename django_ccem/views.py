# Create your views here.
import datetime,json

from django.shortcuts import render, render_to_response
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
from django.core.exceptions import ObjectDoesNotExist
from django.utils.datastructures import MultiValueDictKeyError
from django.contrib.auth.decorators import login_required
import dhis2.settings as dhis2_settings

import rapidsms.router as router

import models as ccem, dhis2.models as dhis2,rapidsms.models as rapid, util, ccem_parser.parser as parser

def base_view(request):
	return render(request, 'ccem_sim/base.html')

@login_required
def contacts(request):
	
	#All connections
	connection_list = rapid.Connection.objects.all()
	
	return render(request, 'contacts.html',{
		'connections':connection_list,
	})

@login_required
def contact(request,identity):
	
	#All Contacts
	contact_list = dhis2.Contact.objects.all()
	
	#All anonymous connections without a contact 
	anonymous_list = rapid.Connection.objects.filter(dhis2=None)
	
	
	#contact details
	connection = util.get_or_none(rapid.Connection,identity=identity)
	if connection is not None:
		try:
			contact_detail = connection.dhis2.contact
			contact_connection = connection.dhis2
		except ObjectDoesNotExist:
			contact_detail, contact_connection = None, None
		#TODO: this will need to be a list off all numbers for the contact
		contact_message_list = ccem.Message.objects.filter(connection__identity=identity)
		
	else:
		contact_detail, contact_message_list = None, None
	
	#POST: Submit Create Form Change
	if request.method == 'POST':
		contact_form = dhis2.ContactForm(instance=contact_detail,data=request.POST)
		if contact_form.is_valid():
			contact_form.save()
			if contact_detail == None:
				contact_form.instance.add_connection(connection)
	else:
		contact_form = dhis2.ContactForm(instance=contact_detail)
		
	return render(request, 'contact.html',{
		'contacts':contact_list,
		'anonymous':anonymous_list,
		'connection':connection,
		'contact':contact_detail,
		'messages':contact_message_list,
		'form':contact_form,
	})

@login_required
def facilities(request):
	facility_id = request.GET.get('id',None)
	facility = util.get_or_none(dhis2.Facility,dhis2_id=facility_id)
	contacts = dhis2.ContactConnection.objects.filter(contact__facility=facility)
	return render(request, 'facilities.html', {
		'facility': facility,
		'contacts':contacts,
		'facility_list':get_facility_list(),
		'parent_org':dhis2.OrganisationUnit.get_root()
	})

def get_facility_list():
	if not getattr(dhis2_settings,'DHIS2_HEIRARCHY_CACHE',True):
		return 'facility_heirarchy.html'
	return 'facility_list_cache.html'

@login_required
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

