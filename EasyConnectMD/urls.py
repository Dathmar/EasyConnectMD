"""EasyConnectMD URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path

from django.conf.urls.static import static
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic.base import RedirectView

urlpatterns = [
    path('favicon.ico', RedirectView.as_view(url=staticfiles_storage.url('img/favicon.ico'))),
    path('apple-touch-icon.png', RedirectView.as_view(url=staticfiles_storage.url('img/apple-touch-icon.png'))),
    path('android-chrome-192x192.png', RedirectView.as_view(url=staticfiles_storage.url('img/android-chrome-192x192.png'))),
    path('android-chrome-512x512.png', RedirectView.as_view(url=staticfiles_storage.url('img/android-chrome-512x512.png'))),
    path('browserconfig.xml', RedirectView.as_view(url=staticfiles_storage.url('img/browserconfig.xml'))),
    path('mstile-150x150.png', RedirectView.as_view(url=staticfiles_storage.url('img/mstile-150x150.png'))),
    path('robots.txt', RedirectView.as_view(url=staticfiles_storage.url('robots.txt'))),
    path('admin/', admin.site.urls),
    path('select2/', include('django_select2.urls')),
    path('', include('EasyConnect.urls')),
]


