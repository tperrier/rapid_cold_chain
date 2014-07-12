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

if __name__ == '__main__':

	print 'Test get children'
	c =  get_children('Skb3RGA4qqD')
	print len(c),c

	print 'Test get children (verbose)'
	c =  get_children('Skb3RGA4qqD',verbose=True)
	print len(c),c
