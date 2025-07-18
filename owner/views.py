from django.shortcuts import render
from django.views import View
from django.shortcuts import render,redirect
from django.views import View
from django.http import HttpResponse
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.auth.mixins import LoginRequiredMixin # ADD THIS INSTEAD
from common.models import Profile,CustomUser
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# Create your views here.
class Ownerhomeview(LoginRequiredMixin,View):
    def get(self,request):
        return render(request, 'owner/ownhom.html')
    



class OwnerClientsView(LoginRequiredMixin, View):
    def get(self, request):
        # Fields needed for CustomUser (client) directly
        customuser_fields = [
            'id', 'first_name', 'last_name', 'email', 'is_active', # Assuming these are directly on CustomUser
            # Add any other CustomUser fields you use in the template
        ]

        # Fields needed from ProfileUser (related via select_related)
        profileuser_fields = [
            'profileuser__profpic', # For the image URL
            'profileuser__bulding',
            'profileuser__floor',
            'profileuser__room',
            'profileuser__phone',
        ]

        # Fields needed from Building (related via select_related)
        building_fields = [
            'profileuser__builing_id__Agent__first_name', # For Agent's first name
            'profileuser__builing_id__Agent__last_name',  # For Agent's last name
        ]

        clients = CustomUser.objects.filter(role='client').select_related(
            'profileuser__builing_id__Agent' # Keep this for efficient joins
        ).only(
            *customuser_fields,
            *profileuser_fields,
            *building_fields
        ).order_by('last_name', 'first_name')
                # --- Pagination Logic ---
        paginator = Paginator(clients, 10)  # Show 10 clients per page. Adjust this number!

        page_number = request.GET.get('page') # Get the current page number from the URL
        try:
            clients = paginator.page(page_number)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            clients = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g., 9999), deliver last page of results.
            clients = paginator.page(paginator.num_pages)
        # --- End Pagination Logic ---

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
        if 'is_active' in request.POST:
            us.is_active = True
        else:
            us.is_active = False
        us.save()
        updated_client = CustomUser.objects.filter(id=id).select_related(
            'profileuser__builing_id__Agent'
        ).first()
        return render(request, 'owner/partials/usrrow.html', {'client': [updated_client]})
    


from django.db.models import Q

class SearchUserView(LoginRequiredMixin, View):
    def get(self, request):
        query = request.GET.get('q', '').strip()
        page_number = request.GET.get('page', 1)

        clients_qs = CustomUser.objects.filter(
            role='client'
        ).select_related(
            'profileuser',
            'profileuser__builing_id',
            'profileuser__builing_id__Agent'
        ).order_by('last_name', 'first_name')

        if query:
            # You can search across multiple fields using Q objects
            clients_qs = clients_qs.filter(
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query) |
                Q(email__icontains=query) |
                Q(profileuser__phone__icontains=query) |
                Q(profileuser__bulding__icontains=query) |
                Q(profileuser__room__icontains=query)
            )
            
        paginator = Paginator(clients_qs, 10)

        try:
            clients = paginator.page(page_number)
        except PageNotAnInteger:
            clients = paginator.page(1)
        except EmptyPage:
            clients = paginator.page(paginator.num_pages)
        
        if not clients.object_list.exists() and query: 
            pass
        return render(request, 'owner/partials/usrrow.html', {'client': clients})