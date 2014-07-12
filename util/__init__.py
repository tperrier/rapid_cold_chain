'''
Collection of utility functions
'''


def get_or_none(cls,**kwargs):
	'''
	Utility function for get or none
	'''
	try:
		return cls.objects.get(**kwargs)
	except cls.DoesNotExist:
		return None
