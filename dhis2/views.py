# Create your views here.

from django.shortcuts import render

import models as dhis2

def facility_list(request):
	facility_list = dhis2.Facility.objects.all()
	if facility_list.count()>0:
		org = facility_list[0]
		levels = facility_list[0].level
		for i in range(0,(levels-1)): org = org.parent
	return render(request, 'facility_heirarchy.html', {'facility_list':org, 'root_id': org.dhis2_id });

