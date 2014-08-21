# Create your views here.

from django.shortcuts import render

import models as dhis2

def facility_list(request):
	root = dhis2.OrganisationUnit.get_root()
	return render(request, 'facility_heirarchy.html', {'parent_org':root});

