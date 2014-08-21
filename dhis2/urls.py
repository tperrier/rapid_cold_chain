from django.conf.urls import patterns, include, url

import views

urlpatterns = [
	url(r'facility_list_cache.html$',views.facility_list),
]
