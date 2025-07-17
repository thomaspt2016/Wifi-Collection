from django.shortcuts import render
from django.views import View
from django.shortcuts import render,redirect
from django.views import View
from django.http import HttpResponse
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.auth.mixins import LoginRequiredMixin # ADD THIS INSTEAD
from common.models import Profile,CustomUser
from django.template.loader import render_to_string

# Create your views here.
class Ownerhomeview(LoginRequiredMixin,View):
    def get(self,request):
        return render(request, 'owner/ownhom.html')
    

class OwnerClientsView(LoginRequiredMixin, View):
    def get(self, request):
        clients = CustomUser.objects.filter(role='client').select_related(
            'profileuser',                      
            'profileuser__builing_id',
            'profileuser__builing_id__Agent'
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

class AcountDisable(LoginRequiredMixin,View):
    def post(self,request,id):
        # 1. Get the specific user
        us = CustomUser.objects.get(id = id)
        
        # 2. Update the user's active status based on the checkbox state
        # The 'value="true"' in your HTML input means 'is_active' will be present in POST if checked.
        # If unchecked, 'is_active' will not be in request.POST.
        if 'is_active' in request.POST:
            us.is_active = True
        else:
            us.is_active = False
        us.save()
        
        # 3. Re-fetch the entire list of clients with updated data
        # This is crucial because hx-target="#tabletaget" expects the full table body content
        clients = CustomUser.objects.filter(role='client').select_related(
            'profileuser',                      
            'profileuser__builing_id',
            'profileuser__builing_id__Agent'
        )
        
        # 4. Render the partial template with the complete, updated list of clients
        # Now only passing 'client' as 'usrrow.html' no longer checks for 'userobjects'
        return render(request, 'owner/partials/usrrow.html', {'client': clients})