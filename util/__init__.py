'''
Collection of utility functions
'''
from django.core.exceptions import MultipleObjectsReturned
import models


def get_or_none(cls,default=None,**kwargs):
	'''
	Utility function for get or none
	'''
	try:
		return cls.objects.get(**kwargs)
	except cls.DoesNotExist:
		return default
	except MultipleObjectsReturned:
		return cls.objects.filter(**kwargs)[0]
		
