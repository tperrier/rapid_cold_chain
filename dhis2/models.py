from django.db import models
from jsonfield import JSONField

import util, dhis2

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
			return '|'.join([' '+i+' ' for i in self.i18n_name.values()])
		return '|'.join([' '+i+' ' for i in self.i18n_name])
	
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

			return cls.objects.get(pk=dhis2_id)
		except cls.DoesNotExist:
			#add loging
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
		
		#Create child organisationUnits if necessary
		if follow_down and 'children' in node and node['children']:
			for child in node['children']:
				cls.create_if_not_exists(child['id'],follow_down=True)
		
		return cls_obj
	
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
	
class Equitment(DHIS2Object,util.models.TimeStampedModel):
	
	facility = models.ForeignKey(Facility,blank=True,null=True)
	
	equitment_type = models.CharField(max_length=50)
	
	working = models.BooleanField(default=True)
	
	dhis2_api_name = 'equipments'
	
class Contact(util.models.TimeStampedModel):
	'''
	A user who interacts with the CCEM system through SMS
	'''
	
	name = models.CharField(max_length=100,blank=True)
	
	language = models.CharField(max_length=5,default='ke')
	
	facility = models.ForeignKey(Facility,blank=True,null=True)
	
	def __unicode__(self):
		return "%s (%s)"%(self.name,self.facility)
	
	@property
	def phone_number(self):
		if self.contact and self.contact.connection_set.count() > 0:
			return self.connection_set.all()[0].identity
		return None
		
class ContactConnection(models.Model):
	'''
	A table to make a ManyToOne connection to between Contact and rapidsms.Connection
	'''
	
	contact = models.ForeignKey(Contact,related_name='connection_set')
	connection = models.OneToOneField('rapidsms.Connection',related_name='dhis2_contact')
	
	def __unicode__(self):
		return '%s (%s)'%(self.contact.name,self.connection)

