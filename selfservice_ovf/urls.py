# selfservice_ovf/urls.py

"""selfservice_ovf URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.urls import path
from django.conf.urls import url, include
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from accounts.forms import LoginForm

urlpatterns = [
    path('admin/', admin.site.urls),
    url('admin/login/', LoginView.as_view(template_name='accounts/login.html', authentication_form=LoginForm), name='admin_login'),
    url(r'ovf/', include('ovf_deployment.urls')),
    url(r'^', include('ovf_deployment.urls')),
    url(r'accounts/', include('accounts.urls')),
    url(r'^login/$', LoginView.as_view(template_name='accounts/login.html', authentication_form=LoginForm), name='root_login'),
    url(r'^logout/$', LogoutView.as_view(next_page='/accounts/login'), name='root_logout'),
]

urlpatterns += staticfiles_urlpatterns()