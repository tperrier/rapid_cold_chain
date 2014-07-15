import api


def from_id(dhis2_id,**kwargs):
	return api.get_from_id('organisationUnits',dhis2_id,**kwargs)

def path_to_root(dhis2_id):
	parents=[]
	n = api.get('organisationUnits/'+dhis2_id,json=True)
	while 'parent' in n and n['parent'] is not None:
		parents.append(n['parent']['id'])
		n = api.get('organisationUnits/'+n['parent']['id'],json=True)
	return parents


def get_children(dhis2_id,verbose=False):
	
	node = api.get('organisationUnits/'+dhis2_id,json=True)
	#Base Case: children is not in node or children is None
	_node = {
		'level':node['level'],
		'id':node['id'],
		'code':node['code'] if 'code' in node else None,
		'name':node['name'],
	}

	if not 'children' in node or node['children'] == None:
		return _node if verbose else None

 	children = {}
	for c in node['children']:
		c_id = c['id']
		children[c_id] = get_children(c_id,verbose)
	_node['children'] = children
	return _node if verbose else children
	
def parse_name(node):
	
	if 'name' not in node:
		return None
	
	#Split name on | and strip all numbers and spaces from beginning and end of each string
	name = [s.strip('0123456789 ') for s in node['name'].split('|')]
	
	if len(name) == 1:
		return {'ke':name[0]}
	elif len(name) > 0:
		return {'lo':'1'+name[0],'ke':name[1]}
		
def has_children(node):
	
	if 'children' not in node:
		return False
	elif len(node['children'])==0:
		return False
	else:
		return True
	
def is_health_facility(node):
	'''
	Returns True if Node is in the Health Facility Group
	Otherwise returns False
	'''
	
	#Level 2 and Level 3 Health Facilities do not have Lao names and have no children
	name = parse_name(node)
	if name and len(name)==1 and not has_children(node):
		return True 
	elif 'organisationUnitGroups' not in node:
		return False
	orgGroups = node['organisationUnitGroups']
	
	def _test(group):
		if 'name' not in group:
			return False
		return group['name'] == 'Health Facility'
		
	group_test = [_test(group) for group in orgGroups]
	
	return True in group_test

if __name__ == '__main__':
	
	id_list = ['Skb3RGA4qqD','lZSTiL43bJ1','FRmrFTE63D0','wbZtszn1b0R']

	for id in id_list:
		node = from_id(id,json=True)
		name = parse_name(node)
		print name
		if 'lo' in name:
			print name['lo']
