

from django import forms
from django.db import models


class PasswordField(forms.CharField):
    """
    Inheritecd from the forms.CharField and adding a widget
    to make a CharField into a PasswordInput field to hide clear text
    """
    widget = forms.PasswordInput


class PasswordModelField(models.CharField):
    """
    This class is to create a new model form field type for passwords
    This isn't built in to the model forms by default
    """
    def formfield(self, **kwargs):
        defaults = {'form_class': PasswordField}
        defaults.update(kwargs)
        return super(PasswordModelField, self).formfield(**defaults)
