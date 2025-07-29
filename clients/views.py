from django.shortcuts import render
from django.views import View
from django.shortcuts import render,redirect
from django.views import View
from django.http import HttpResponse
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.mixins import LoginRequiredMixin
from common import models

class ClientHomeView(LoginRequiredMixin,View):#this is where dashboard codes comes in
    def get(self,request):
        return render(request, 'client/clienthome.html')


class WificodesView(LoginRequiredMixin, View):
    def get(self, request):
        usr = request.user
        print(usr.id)
        codes = models.CodePoool.objects.filter(assignedto = usr)
        print(codes)
        return render(request, 'client/cliwificode.html',{'codeobject':codes})
    
class CurrentBillView(LoginRequiredMixin, View):
    def get(self, request):
        planobj = models.InternetPlan.objects.all()
        print(planobj)
        return render(request, 'client/clibill.html',{'plan': planobj})
    
class PaymenHistoryView(LoginRequiredMixin,View):
    def get(self, request):
        return render(request, 'client/payhist.html')
    
class RaiseTicketView(LoginRequiredMixin,View):
    def get(self, request):
        return render(request, 'client/ticket.html')

class FAQView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'client/faq.html')

class ContactAgentView(LoginRequiredMixin,View):
    def get(self,request):
        return render(request, 'client/agent.html')