from django.db import models
from jsonfield import JSONField

import util.models as util

# Create your models here.

class DHIS2Object(models.Model):
	
	dhis2_id = models.CharField(max_length=20,primary_key=True) 
	
	class Meta:
		abstract = True

class OrganisationBase(DHIS2Object,util.TimeStampedModel):
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
	
	dhis2_code = models.CharField(max_length=20)
	
	level = models.IntegerField() 
	
	class Meta:
		abstract = True
		
	def __unicode__(self):
		return '|'.join([' '+i+' ' for i in self.i18n_name.values()])
	
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
	
class Equitment(DHIS2Object,util.TimeStampedModel):
	
	facility = models.ForeignKey(Facility,blank=True,null=True)
	
	equitment_type = models.CharField(max_length=50)
	
	working = models.BooleanField(default=True)
	
	dhis2_api_name = 'equipments'

class ContactProfile(util.TimeStampedModel):
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
