from django.shortcuts import render
from functools import reduce
from django.core import exceptions
from django.http import HttpResponse
from rest_framework import generics, status
from rest_framework.views import APIView, View
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.urls import reverse


class SignupView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = "accounts/signup.html"

    def get(self, request):
        return Response(template_name=self.template_name)


class LoginView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = "accounts/login.html"

    def get(self, request):
        return Response(template_name=self.template_name)


# @method_decorator(login_required(login_url=reverse('login').lstrip('/')), name='dispatch')
class HomePage(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = "ovf/index.html"

    def get(self, request):
        return Response(template_name=self.template_name)
