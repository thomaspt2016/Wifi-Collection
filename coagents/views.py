from django.shortcuts import render
from django.views import View
from django.shortcuts import render,redirect
from django.views import View
from django.http import HttpResponse
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.mixins import LoginRequiredMixin


class CoHomeView(LoginRequiredMixin,View):
    def get(self,request):
        return render(request, 'coagent/cohome.html')
    
class CoClientsView(LoginRequiredMixin,View):
    def get(self, request):
        return render(request, 'coagent/coclients.html')