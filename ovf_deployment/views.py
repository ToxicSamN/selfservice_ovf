# ovf_deployment/views.py

import random
# import logging
from django.views import View
from django.urls import reverse
from django.shortcuts import render, render_to_response
from ovf_deployment.quotes import QUOTES
from ovf_deployment.forms import DynamicForm, InitialForm
from ovf_deployment.log.setup import addClassLogger
from django.template.defaulttags import register
from formtools.wizard.views import SessionWizardView, CookieWizardView
from ovf_deployment.forms import InitialForm, EulaForm, NameFolderTreeForm


# log = logging.getLogger(__name__)


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@addClassLogger
class WizardView(SessionWizardView):
    template_name = 'ovf_deployment/wizard.html'

    def done(self, form_list, **kwargs):
        # self.__log.debug('Done')
        form_data = [form.cleaned_data for form in form_list]
        return render_to_response('ovf_deployment/done.html', {'form_data': form_data})


#@addClassLogger
class OvfSelfService(View):
    greeting = "Hello World!"
    my_name = "Sammy Shuck"
    some_list = ['Heya', 'Whoa', 333, 444, 'Yipee']

    def get(self, request):
        # self.__log.debug(f'OvfSelfService Class get() method')
        form = InitialForm()
        # form_obj = TemplateForm(form, 'myform', 1)
        quote = QUOTES[random.randint(0, len(QUOTES)-1)]
        data = {'my_name': self.my_name,
                'greeting': self.greeting,
                'a_list': self.some_list,
                'home': True,
                'quote': quote,
                'form': form,
                }
        return render(request, template_name='ovf_deployment/index.html', context=data)


# @addClassLogger
class OvfTasks(View):

    greeting = "Hello World!"
    my_name = "Sammy Shuck"
    some_list = ['I', 'Have', 'Some', 'tasks', 'to', 'show']

    def get(self, request):
        quote = QUOTES[random.randint(0, len(QUOTES) - 1)]
        data = {'my_name': self.my_name, 'greeting': self.greeting, 'a_list': self.some_list, 'tasks': True, 'quote': quote}
        return render(request, template_name='ovf_deployment/tasks/index.html', context=data)
