'''
Collection of utility functions
'''

import models


def get_or_none(cls,default=None,**kwargs):
	'''
	Utility function for get or none
	'''
	try:
		return cls.objects.get(**kwargs)
	except cls.DoesNotExist:
		return default
