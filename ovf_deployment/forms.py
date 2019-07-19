#  ovf_deployment/forms.py

# import logging
from django import forms
from ovf_deployment.log.setup import addClassLogger


# log = logging.getLogger(__name__)


# @addClassLogger
class TemplateForm:

    def __init__(self, form, name, num):
        form = form
        name = name
        num = num


# @addClassLogger
class InitialForm(forms.Form):
    vcenter = forms.CharField(max_length=100)


# @addClassLogger
class EulaForm(forms.Form):
    eula = forms.CharField(max_length=100)


# @addClassLogger
class NameFolderTreeForm(forms.Form):
    eula2 = forms.CharField(max_length=100)


# @addClassLogger
class NetworkForm(forms.Form):
    pass


# @addClassLogger
class DynamicForm(forms.Form):
    post = forms.CharField()
