from django.conf.urls import patterns, include, url

from views import *

urlpatterns = [
	url(r'^$',messages),
	url(r'messages/$',messages),
	url(r'contacts/$',contacts),
	url(r'facilities/$',facilities),
]
