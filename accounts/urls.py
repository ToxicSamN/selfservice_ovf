from django.conf.urls import url, include
from django.contrib.auth.views import LoginView, LogoutView
from .views import SignupView, HomePage
from accounts.forms import LoginForm
from django.contrib.auth.forms import AuthenticationForm

app_name = 'accounts'

urlpatterns = [
    url(r'^signup/$', SignupView.as_view(), name="signup"),
    url(r'^login/$', LoginView.as_view(template_name='accounts/login.html', authentication_form=LoginForm), name='login'),
    url(r'^logout/$', LogoutView.as_view(next_page='/accounts/login'), name='logout'),
    url(r'^$', HomePage.as_view(), name='home')
]