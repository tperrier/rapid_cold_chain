from django.conf.urls import patterns, url

import views


urlpatterns = [
	url(r"^$", views.EnvayaView.as_view()),
	url(r"^test_receive/?",views.ReceiveView.as_view()),
	url(r"^test_send/?",views.SendView.as_view()),
	url(r"^training/?",views.training_view),
]
