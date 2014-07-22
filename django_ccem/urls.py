from django.conf.urls import patterns, include, url

from views import *

urlpatterns = patterns('',
	url(r'^$',base_view),
	url(r'messages/$',messages),
	url(r'contacts/$',contacts),
	url(r'facilities/$',facilities),
)
