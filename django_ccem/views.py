# Create your views here.


from django.shortcuts import render

def base_view(request):
	return render(request, 'ccem_sim/base.html')
	
def custom_view(request):
	return render(request, 'custom.html')
