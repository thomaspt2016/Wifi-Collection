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
    

class OwnerClientsView(LoginRequiredMixin, View):
    def get(self, request):
        # Fetch CustomUser objects (clients) and prefetch related Profile, Building, and Agent data.
        # 'profileuser' is the related_name from CustomUser to Profile.
        # 'building' is the related_name from Profile to Building.
        # 'Agent' is the field name on Building that links to CustomUser.
        clients = CustomUser.objects.filter(role='client').select_related(
            'profileuser',                      # Prefetches the Profile object for each CustomUser
            'profileuser__builing_id',         # Prefetches the Building object linked via profileuser's building_id ForeignKey
            'profileuser__builing_id__Agent'   # Prefetches the Agent (CustomUser) object linked via the Building's Agent ForeignKey
        )
        return render(request, 'owner/clients.html', {'client': clients})

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