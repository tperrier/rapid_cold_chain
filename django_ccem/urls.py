from django.conf.urls import patterns, include, url

import views

urlpatterns = [
	url(r'^$','django_ccem.views.messages'),
	url(r'^messages/$','django_ccem.views.messages'),
	url(r'^contact/$','django_ccem.views.contacts'),
	url(r'^contact/(?P<identity>\+?[0-9]{1,15})/$','django_ccem.views.contact'),
	url(r'^facilities/$','django_ccem.views.facilities'),
]
