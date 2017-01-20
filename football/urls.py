"""football URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
import debug_toolbar
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin
from django.conf.urls.i18n import i18n_patterns

from teams import views
from football import settings

urlpatterns = i18n_patterns(
    url(r'^$', views.index, name='home'),
    url(r'^admin/', admin.site.urls),
    url(r'^__debug__/', include(debug_toolbar.urls)),
    url(r'^auth/', include("authsys.urls", namespace='authsys')),
    url(r'^article/', include("article.urls", namespace='article')),
    url(r'^', include("teams.urls", namespace='teams')),
    url(r'^i18n/', include('django.conf.urls.i18n'), name="set_language"),
)# + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
