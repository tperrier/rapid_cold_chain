from django.db import models
from django import forms
from django.db.models import signals
from django.dispatch import receiver
from django.core.exceptions import ObjectDoesNotExist

from django.utils.safestring import mark_safe
from django.utils.html import conditional_escape, format_html
import django.utils.timezone as timezone
from django.forms.util import flatatt, to_current_timezone
from django.utils.encoding import force_text

from jsonfield import JSONField
import rapidsms.models as rapidsms

import util, dhis2, logging,code, datetime
import django_ccem.models as ccem

logger = logging.getLogger(__name__)
#~ logger = logging.getLogger('none')

# Create your models here.

class DHIS2Object(models.Model):
	
	dhis2_id = models.CharField(max_length=20,primary_key=True) 
	
	class Meta:
		abstract = True

class OrganisationBase(DHIS2Object,util.models.TimeStampedModel):
	"""
	Abstract class definition for element in the Organisational Hierarchy
	"""
	
	'''
	A Json object representing the OrganisationUnits name in multiple languages
	formate {
		'ke':
		'lo':
	}
	'''
	i18n_name = JSONField()
	
	dhis2_code = models.CharField(max_length=20,null=True,blank=True)
	
	level = models.IntegerField() 
	
	class Meta:
		abstract = True
		
	def __unicode__(self):
		if isinstance(self.i18n_name,dict):
			return '|'.join([' '+i.capitalize()+' ' for i in self.i18n_name.values()])
		return '|'.join([' '+i.capitalize()+' ' for i in self.i18n_name])
	
	@classmethod
	def create_if_not_exists(cls,dhis2_id,follow_up=False,follow_down=False):
		'''
		Uses the DHIS2 API to add a facility to the local database
		@cls: OrganisationUnit or Facility (calling class)
		@dhis2_id: the dhis2 id to add
		@follow_up: add parent nodes on path to root if needed
		@follow_down: add all decedent nodes if needed
		
		Since dhis2.orgs.is_health_facility() is not always accurate this
		method may create some Facilities as OrganisationUnits
		'''
		#Create parent organisationUnits if necessary 
		if follow_up:
				path_to_root = dhis2.orgs.path_to_root(dhis2_id)
				path_to_root.reverse()
				for p in path_to_root:
					OrganisationUnit.create_if_not_exists(p)
		
		#Create this unit if no OrgUnit of Facility alread exists with that id
		orgs = OrganisationUnit.objects.filter(pk=dhis2_id)
		facs = Facility.objects.filter(pk=dhis2_id)
		if not (orgs or facs):
			logger.debug('Creating OrgansationUnit %s'%dhis2_id)
			node = dhis2.orgs.from_id(dhis2_id,json=True)
			#read node information
			_id = node['id']
			_code = node['code'] if 'code' in node else None
			_level = node['level']
			_name = dhis2.orgs.parse_name(node)
			_parent = node['parent']['id'] if node['parent'] else None
			
			#set cls var to the correct class based on Facility type
			cls = Facility if dhis2.orgs.is_health_facility(node) else OrganisationUnit
			
			cls_obj = cls(
				dhis2_id=_id,
				dhis2_code=_code,
				level=_level,
				i18n_name=_name,
				parent=util.get_or_none(OrganisationUnit,pk=_parent),
				)
			cls_obj.save()
		else:
			cls_obj = orgs[0] if orgs else facs[0] # set cls_obj to already existing OrgUnit
			logger.debug('OrganizationUnit %s already exits'%cls_obj)
		
		#Create child organisationUnits if necessary
		if follow_down and 'children' in node and node['children']:
			for child in node['children']:
				cls.create_if_not_exists(child['id'],follow_down=True)
		
		return cls_obj
		
	@classmethod
	def get_root(cls):
		root = OrganisationUnit.objects.filter(parent=None)
		if root.count()>0:
			return root[0]
		return None
	
class OrganisationUnit(OrganisationBase):
	"""
	An organizational unit in the hierarchy that is not a facility 
	"""
	#The parent of this entity in the hierarchy.  If blank, indicates a root node
	parent = models.ForeignKey('self',blank=True,null=True,related_name='children')
	
	#API Name for access to DHIS2
	dhis2_api_name = 'organisationUnits'
	
class FacilityQuerySet(models.QuerySet):
	
	def non_reporting(self,month=None):
		return self.get_query_set().exclude(dhis2_id__in=self.reporting(month))
		
	def reporting(self,month=None):
		today = datetime.date.today()
		if month is None:
			start = datetime.date(today.year,today.month,1)
		elif isinstance(month,tuple):
			start = datetime.date(month[0],month[1],1)
		else:
			start = util.get_month_offset(today,month*-1)
		
		#add some buffer
		start = start - datetime.timedelta(days=5)
		end = start + datetime.timedelta(days=25)
		
		return self.filter(
			contact__connection__messages__created__range=(start,end),
			contact__connection__messages__is_submission=True
		).distinct()
		
	def facility_groups(cls):
		facilities = Facility.objects.all()
		groups = {}
		for f in facilities:
			try:
				groups[f.parent].append(f)
			except KeyError as e:
				groups[f.parent] = [f]
		return groups
	
		
class GetMessagesByMonthMixin(object):
	
	def get_messages_by_month(self,start=None,end=None,direction=None,submission=None):
		'''
		Return all messages based on month offset
			start: if tuple (yyyy,mm) if, int i months back, if none start of the current month.
			end: number of months to count. 
			direction: 'I','O' or None for no filter.
			
			By default gets the messages for the current month
		'''
		today = datetime.date.today()
		if start is None:
			start = datetime.date(today.year,today.month,1)
		elif isinstance(start,tuple):
			start = datetime.date(start[0],start[1],1)
		else:
			start = util.get_month_offset(today,start*-1)
			
		if end == None:
			end = util.get_month_offset(today,1)
		elif isinstance(end,tuple):
			end = datetime.date(end[0],end[1],1)
		else:
			end = util.get_month_offset(start,end)
			
		return self.get_messages(start,end,direction,submission)
		
	def date_filter_messages(self,start=None,end=None,direction=None,submission=None):
		'''
		Return all messages for contact based on parameters:
			start: the date to start on or None for no filter 
			end: the date to end on or None for no filter
			direction: the direction of messages.  'I','O' or None for no filter
		'''
		
		if start is not None:
			messages = messages.filter(created__gte=start)
		if end is not None:
			messages = messages.filter(created__lte=end)
		if direction is not None:
			messages = messages.filter(direction=direction)
		if submission is not None:
			messages = messages.filter(is_submission=submission)
		
		return messages
		
	
class Facility(OrganisationBase,GetMessagesByMonthMixin):
	
	#The parent hierarchy related Manager is OrganisationUnit.facility_set.all()
	parent = models.ForeignKey(OrganisationUnit,blank=True,null=True)
	
	dhis2_api_name = 'organisationUnits'
	
	#set default manager
	objects = FacilityQuerySet.as_manager()
	
	def get_messages(self,start=None,end=None,direction=None,submission=None):
		'''
		Use GetMessagesByMonthMixin to return filtered messages
		'''
		messages = ccem.Message.objects.filter(connection__dhis2__contact__facility=self)
		return self.date_filter_messages(messages)
		
	def last_report(self):
		try:
			return self.report_set.order_by('-created')[0]
		except IndexError as e:
			return None
	
class Equitment(DHIS2Object,util.models.TimeStampedModel):
	
	LABEL_CHOICES = [(chr(c),chr(c).capitalize()) for c in range(ord('a'),ord('z')+1)]
	
	facility = models.ForeignKey(Facility,blank=True,null=True)
	
	equitment_type = models.CharField(max_length=50)
	
	working = models.BooleanField(default=True)
	
	#Value for SMS reference to refrigerator
	label = models.CharField(max_length=1,choices=LABEL_CHOICES,blank=True,null=True)
	
	dhis2_api_name = 'equipments'
	
class Contact(util.models.TimeStampedModel,GetMessagesByMonthMixin):
	'''
	A user who interacts with the CCEM system through SMS
	'''
	
	I18N_EN = 'en'; I18N_KA = 'ka'; I18N_LA = 'la'; I18N_TH = 'th'
	LANGUAGE_CHOICES = ((I18N_EN,'English'),(I18N_KA,'Karaoke'),(I18N_LA,'Lao'),(I18N_TH,'Thai'))
	
	name = models.CharField(max_length=100,blank=True)
	
	language = models.CharField(max_length=5,default=I18N_KA,choices=LANGUAGE_CHOICES)
	
	facility = models.ForeignKey(Facility,blank=True,null=True)
	
	connection = models.OneToOneField(rapidsms.Connection,blank=True,null=True,related_name='dhis2')
	
	email = models.EmailField(blank=True,null=True)
	
	def add_connection(self,connection):
		self.connection = connection
		self.save()
	
	def phone_number(self):
		if self.connection:
			return self.connection.identity
		return None
			
	def last_submission(self):
		try:
			return ccem.Message.objects.filter(is_submission=True,connection=self.connection).order_by('-created')[0]
		except IndexError as e:
			return None
	
	def get_messages(self,start=None,end=None,direction=None,submission=None):
		'''
		Use GetMessagesByMonthMixin to return filtered messages
		'''
		messages = ccem.Message.objects.filter(connection=self.connection)
		
		return self.date_filter_messages(messages)
		
	def __unicode__(self):
		return "%s (%s)"%(self.name,self.facility)
		
	@classmethod
	def from_connection(cls,connection):
		'''
		Return a Contact from a connection
		'''
		try:
			return connection.contact
		except ObjectDoesNotExist as e:
			return None
			
	@classmethod
	def from_identity(cls,identity):
		'''
		Return a Contact from a phonenumber (identity)
		'''
		from rapidsms.models import Connection
		try:
			conn = Connection.objects.get(identity=identity)
			return cls.from_connection(conn)
		except Connection.DoesNotExist as e:
			return None

class FacilitySelect(forms.Select):
	
	def __init__(self, attrs=None, choices=()):
		super(FacilitySelect, self).__init__(attrs)
		# choices can be any iterable, but we may need to render this widget
		# multiple times. Thus, collapse it into a list so it can be consumed
		# more than once.
		self.choices = list(choices)
	
	def render(self, name, value, attrs=None, choices=()):
		if value is None:
			value = ''
		final_attrs = self.build_attrs(attrs, name=name)
		output = [format_html('<select{0}>', flatatt(final_attrs))]
		output.append('<option value="">---------</option>')
		
		options = self.render_options(value)
		if options:
			output.append(options)
		
		output.append('</select>')
		return mark_safe('\n'.join(output)) 
		
	def render_options(self,value):
		output = []
		value = [force_text(value)]
		for parent, facilities in Facility.objects.facility_groups().iteritems():
			if isinstance(facilities, (list, tuple)):
				output.append(u'<optgroup label="%s">'%parent)
				for facility in facilities:
					output.append(self.render_option(value, str(facility.dhis2_id),unicode(facility)))
				output.append(u'</optgroup>')
		return u'\n'.join(output).encode('utf-8').decode('utf-8')

class ContactForm(forms.ModelForm):
	
	class Meta:
		model = Contact
		widgets = {
			'facility':FacilitySelect()
		}
		fields = '__all__'
	
"""
class ContactConnection(models.Model):
	'''
	A table to make a ManyToOne connection to between Contact and rapidsms.Connection
	'''
	
	contact = models.ForeignKey(Contact,related_name='connection_set')
	connection = models.OneToOneField('rapidsms.Connection',related_name='dhis2')
	
	def __unicode__(self):
		return '%s (%s)'%(self.contact.name,self.connection)
	
	@property
	def identity(self):
		return self.connection.identity
		
	@property
	def backend(self):
		return self.connection.backend
"""
