from django.conf.urls import patterns, url
from docs import views

urlpatterns = patterns('',
		url(r'^$', views.main, name='main'),
		url(r'^new$', views.create, name='create'),
		url(r'^folder/(?P<nidb64>[0-9A-Za-z_\-]+)$', views.folder, name='folder'), 
		url(r'^view/(?P<nidb64>[0-9A-Za-z_\-]+)$', views.view, name='view'), 
		url(r'^edit/(?P<nidb64>[0-9A-Za-z_\-]+)$', views.edit, name='edit'), 
	)
