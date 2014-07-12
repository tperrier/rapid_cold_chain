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
		try:
			return cls.objects.get(pk=dhis2_id)
		except cls.DoesNotExist:
			
			if follow_up:
				path_to_root = dhis2.orgs.path_to_root(dhis2_id)
				path_to_root.reverse()
				for p in path_to_root:
					OrganisationUnit.create_if_not_exists(p)
					
			node = dhis2.orgs.from_id(dhis2_id,json=True)
			#read node information
			_id = node['id']
			_code = node['code'] if 'code' in node else None
			_level = node['level']
			_name = node['name'] if 'name' in node else None
			_parent = node['parent']['id'] if node['parent'] else None
			
			cls_obj = cls(
				dhis2_id=_id,
				dhis2_code=_code,
				level=_level,
				i18n_name=[_name],
				parent=util.get_or_none(OrganisationUnit,pk=_parent),
				)
			cls_obj.save()
			print cls_obj
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

class ContactProfile(util.models.TimeStampedModel):
	'''
	A user who interacts with the CCEM system through SMS
	'''
	
	contact = models.OneToOneField('rapidsms.Contact',primary_key=True)
	
	facility = models.ForeignKey(Facility,blank=True,null=True)
	
	
	@property
	def phone_number(self):
		if self.contact and self.contact.connection_set.count() > 0:
			return self.connection_set.all()[0].identity
		return None
