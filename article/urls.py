from django.conf.urls import url
from .views import *

urlpatterns = [
    url(r'^$', ArticleListView.as_view(), name="article-list"),
    url(r'^create/$', ArticleCreateView.as_view(), name="article-create"),
    url(r'^edit/(?P<pk>\d+)/$', ArticleUpdateView.as_view(), name="article-update"),
    url(r'^delete/(?P<pk>\d+)/$', ArticleDeleteView.as_view(), name="article-delete"),
    url(r'^(?P<pk>\d+)/$', ArticleDetailView.as_view(), name="article-detail"),
]
