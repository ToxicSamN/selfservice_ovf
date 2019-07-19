# ovf_deployment/urls.py

from django.conf.urls import url, include
from rest_framework.urlpatterns import format_suffix_patterns
from ovf_deployment.views import OvfSelfService, OvfTasks, WizardView
# from ovf_deployment.forms import InitialForm, EulaForm, NameFolderTreeForm



urlpatterns = {
    # REST Patterns for all users
    # url(r'accounts/', include('accounts.urls')),
    url(r'^$', OvfSelfService.as_view(), name="ovf_selfsvc"),
    url(r'tasks/', OvfTasks.as_view(), name="ovf_tasks"),
    url(r'wizard/', WizardView.as_view(), name="ovf_wizard"),
}

urlpatterns = format_suffix_patterns(urlpatterns)
