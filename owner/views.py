from django.shortcuts import render
from django.views import View
from django.shortcuts import render,redirect
from django.views import View
from django.http import HttpResponse
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.auth.mixins import LoginRequiredMixin # ADD THIS INSTEAD
from common.models import Profile,CustomUser

# Create your views here.
class Ownerhomeview(LoginRequiredMixin,View):
    def get(self,request):
        return render(request, 'owner/ownhom.html')
    

class OwnerClientsView(LoginRequiredMixin,View):
    def get(self,request):
        clint = CustomUser.objects.filter(role='client')
        return render(request, 'owner/clients.html',{'client':clint})

class CollectionAgentsView(LoginRequiredMixin,View):
    def get(self,request):
        return render(request, 'owner/colla.html')

class InternetplansView(LoginRequiredMixin,View):
    def get(self, request):
        return render(request, 'owner/intrplans.html')
    
class CodeUploadView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'owner/codup.html')
    
class CodePoolStatView(LoginRequiredMixin,View):
    def get(self,request):
        return render(request, 'owner/codepoo.html')
    
class PaymentsView(LoginRequiredMixin,View):
    def get(self,request):
        return render(request, 'owner/payments.html')
    
class ReportsView(LoginRequiredMixin,View):
    def get(self,request):
        return render(request, 'owner/fiinreport.html')
    
class GeneralSettingView(LoginRequiredMixin,View):
    def get(self,request):
        return render(request, 'owner/systemset.html')
    
class APISettingView(LoginRequiredMixin,View):
    def get(self,request):
        return render(request, 'owner/apiset.html')