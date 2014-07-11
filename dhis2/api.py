import requests,json,code
import settings

url = settings.DHIS2_API_URL

ses = requests.Session()
ses.auth = (settings.DHIS2_USERNAME,settings.DHIS2_PASSWORD)
ses.headers.update({'Accept':'application/json'})	

def get(api_call,**kwargs):
	r = ses.get(url+api_call)
	if 'json' in kwargs and kwargs['json']:
		return r.json()
	return r

def get_from_id(api_object,dhis2_id,**kwargs):
	return get(api_object+'/'+dhis2_id,**kwargs)

def get_eq(eq_id,**kwargs):
	return get('equipments/'+eq_id,**kwargs)

def get_facility_eq(facility_id,**kwargs):
	return get('equipments?ou='+facility_id,**kwargs)



if __name__ == '__main__':
	''' Basic Testing'''
	print 'Test ref'
	print get_facility_eq('tFie49aXcSb',json=True)

	print 'Test get'
	print get('organisationUnits/W6sNfkJcXGC')

	print 'Test get_from_id'
	print get_from_id('organisationUnits','W6sNfkJcXGC')

	print 'Test with json'
	j =  get_from_id('organisationUnits','W6sNfkJcXGC',json=True)
	print len(j),j.keys()[:10]

