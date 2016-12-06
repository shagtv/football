from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name="list"),
    url(r'^(?P<name>[\w-]+)/$', views.detail, name="detail"),
    url(r'^(?P<id>\d+)/edit/$', views.update, name="update"),
    url(r'^(?P<id>\d+)/delete/$', views.delete, name="delete"),
]
