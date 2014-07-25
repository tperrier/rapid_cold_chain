from django.conf.urls import patterns, include, url

from views import *

urlpatterns = patterns('',
	url(r'^$',messages),
	url(r'messages/$',messages),
	url(r'contacts/$',contacts),
	url(r'facilities/$',facilities),
	url(r'facility_list.html$',facility_list),
)
