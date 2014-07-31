from django.conf.urls import patterns, url
from . import views


urlpatterns = [
	url(r"^$", views.EnvayaView.as_view(backend_name="envaya")),
	url(r"^test/?",views.TestView.as_view()),
]
