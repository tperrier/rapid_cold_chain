from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin

admin.autodiscover()

rapidsms_urls = [
	# RapidSMS contrib app URLs
	url(r'^$','rapidsms.views.dashboard',name='rapidsms_home'),
	url(r'^httptester/', include('rapidsms.contrib.httptester.urls')),
	#(r'^locations/', include('rapidsms.contrib.locations.urls')),
	url(r'^messagelog/', include('rapidsms.contrib.messagelog.urls')),
	url(r'^messaging/', include('rapidsms.contrib.messaging.urls')),
	url(r'^registration/', include('rapidsms.contrib.registration.urls')),
	# Third party URLs
	url(r'^selectable/', include('selectable.urls')),
]

urlpatterns = [
	url(r'^admin/', include(admin.site.urls)),
	# RapidSMS core URLs
	url(r'^accounts/', include('rapidsms.urls.login_logout')),
	#Custom URLS
	url(r'^dhis2/',include('dhis2.urls')),
	url(r'',include('django_ccem.urls')),
	url(r'^rapidsms/',include(rapidsms_urls)),
	url(r'^envaya/',include('envaya.urls')),
	url(r'^test_message/$','ccem_parser.views.test_message'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
#urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


if 'rosetta' in settings.INSTALLED_APPS:
	urlpatterns += [url(r'^rosetta/', include('rosetta.urls'))]
