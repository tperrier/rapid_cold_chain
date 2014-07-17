from django.conf.urls import patterns, include, url

from views import *

urlpatterns = patterns('',
	url(r'^$',base_view),
	url(r'c.*$',custom_view),
	url(r'messages$',messages),
	url(r'messages/regular',messages,{"filter":"regular"}),
	url(r'messages/submission',messages,{"filter":"submission"}),
)
