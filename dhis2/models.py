from django.db import models
from django import forms
from django.db.models import signals
from django.dispatch import receiver
from django.core.exceptions import ObjectDoesNotExist

from django.utils.safestring import mark_safe
from django.utils.html import conditional_escape, format_html
from django.forms.util import flatatt, to_current_timezone
from django.utils.encoding import force_text

from jsonfield import JSONField

import util, dhis2, logging

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
		
		#Create this unit if necessary
		try:

			cls_obj = cls.objects.get(pk=dhis2_id)
		except cls.DoesNotExist:
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
	
	
class Facility(OrganisationBase):
	
	#The parent hierarchy related Manager is OrganisationUnit.facility_set.all()
	parent = models.ForeignKey(OrganisationUnit,blank=True,null=True)
	
	dhis2_api_name = 'organisationUnits'
	
	@classmethod
	def get_facility_groups(cls):
		facilities = Facility.objects.all()
		groups = {}
		for f in facilities:
			try:
				groups[unicode(f.parent)].append(f)
			except KeyError as e:
				groups[unicode(f.parent)] = [f]
		return groups
	
class Equitment(DHIS2Object,util.models.TimeStampedModel):
	
	LABEL_CHOICES = [(chr(c),chr(c).capitalize()) for c in range(ord('a'),ord('z')+1)]
	
	facility = models.ForeignKey(Facility,blank=True,null=True)
	
	equitment_type = models.CharField(max_length=50)
	
	working = models.BooleanField(default=True)
	
	#Value for SMS reference to refrigerator
	label = models.CharField(max_length=1,choices=LABEL_CHOICES,blank=True,null=True)
	
	dhis2_api_name = 'equipments'
	
class Contact(util.models.TimeStampedModel):
	'''
	A user who interacts with the CCEM system through SMS
	'''
	
	I18N_EN = 'en'; I18N_KA = 'ka'; I18N_LA = 'la'; I18N_TH = 'th'
	LANGUAGE_CHOICES = ((I18N_EN,'English'),(I18N_KA,'Karaoke'),(I18N_LA,'Lao'),(I18N_TH,'Thai'))
	
	name = models.CharField(max_length=100,blank=True)
	
	language = models.CharField(max_length=5,default=I18N_KA,choices=LANGUAGE_CHOICES)
	
	facility = models.ForeignKey(Facility,blank=True,null=True)
	
	email = models.EmailField(blank=True,null=True)
	
	def add_connection(self,connection):
		ContactConnection.objects.create(contact=self,connection=connection)
	
	@property
	def phone_number(self):
		if self.connection_set.count() > 0:
			return self.connection_set.all()[0].connection.identity
		return None
		
	def __unicode__(self):
		return "%s (%s)"%(self.name,self.facility)
		
	@classmethod
	def from_connection(cls,conn):
		try:
			return conn.dhis2.contact
		except ObjectDoesNotExist as e:
			return None
			
	@classmethod
	def from_identity(cls,identity):
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
		for parent, facilities in Facility.get_facility_groups().iteritems():
			if isinstance(facilities, (list, tuple)):
				output.append('<optgroup label="%s">'%parent)
				for facility in facilities:
					output.append(self.render_option(value, unicode(facility.dhis2_id),unicode(facility)))
				output.append('</optgroup>')
		return '\n'.join(output)
			
class ContactForm(forms.ModelForm):
	
	class Meta:
		model = Contact
		widgets = {
			'facility':FacilitySelect()
		}
	

class ContactConnection(models.Model):
	'''
	A table to make a ManyToOne connection to between Contact and rapidsms.Connection
	'''
	
	contact = models.ForeignKey(Contact,related_name='connection_set')
	connection = models.OneToOneField('rapidsms.Connection',related_name='dhis2')
	
	def __unicode__(self):
		return '%s (%s)'%(self.contact.name,self.connection)
		
	
