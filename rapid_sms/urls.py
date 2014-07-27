from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
	url(r'^admin/', include(admin.site.urls)),
	# RapidSMS core URLs
	(r'^accounts/', include('rapidsms.urls.login_logout')),
	url(r'^$', 'django_ccem.views.messages', name='rapidsms-dashboard'),
	# RapidSMS contrib app URLs
	(r'^httptester/', include('rapidsms.contrib.httptester.urls')),
	#(r'^locations/', include('rapidsms.contrib.locations.urls')),
	(r'^messagelog/', include('rapidsms.contrib.messagelog.urls')),
	(r'^messaging/', include('rapidsms.contrib.messaging.urls')),
	(r'^registration/', include('rapidsms.contrib.registration.urls')),
	# Third party URLs
	(r'^selectable/', include('selectable.urls')),
	
	#Custom URLS
	(r'^moderation/',include('django_ccem.urls')),
	(r'^dhis2/',include('dhis2.urls')),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
#urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


if 'rosetta' in settings.INSTALLED_APPS:
	urlpatterns += patterns('',
		url(r'^rosetta/', include('rosetta.urls')),
	)
