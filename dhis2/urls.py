from django.conf.urls import patterns, include, url

from views import *

urlpatterns = [
	url(r'facility_list_cache.html$',facility_list),
]
