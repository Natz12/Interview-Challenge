from django.conf.urls import url
from django.views.generic import TemplateView
from . import views

urlpatterns = [
	url(r'^info/', views.info, name='info'),
	url(r'^needs_remote/', views.needs_remote),
	url(r'^chart/', TemplateView.as_view(template_name="portfolios/chart.html"), name='chart'),
	url(r'^$', views.index, name='index'),
]
