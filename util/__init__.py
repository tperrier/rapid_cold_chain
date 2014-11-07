'''
Collection of utility functions
'''
from django.core.exceptions import MultipleObjectsReturned
import models, datetime


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
		
def get_month_offset(date,offset):
	m = (date.month + offset) % 12 or 12
	y = date.year + ((date.month)+offset-1) // 12
	return datetime.date(y,m,1)
		
