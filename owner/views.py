from django.shortcuts import render
from django.views import View
from django.shortcuts import render,redirect
from django.views import View
from django.http import HttpResponse
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.auth.mixins import LoginRequiredMixin # ADD THIS INSTEAD
from common.models import Profile,CustomUser,Building,InternetPlan
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q,Count
from common.forms import InternetPlanForm

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

class CollectionAgentsView(LoginRequiredMixin, View):
    def get(self, request):
        collection_agents = CustomUser.objects.filter(role='coagent')

        # Create a list of dictionaries, where each dictionary contains
        # an agent object and their unique building names
        agents_data = []
        for agent in collection_agents:
            # Use values_list to get only the 'building_name', then flat=True for a simple list,
            # and finally distinct() to ensure unique names.
            unique_building_names = agent.buildings_managed.all().values_list('building_name', flat=True).distinct()
            
            agents_data.append({
                'agent': agent,
                'unique_buildings': unique_building_names
            })

        # Pass this prepared data to your template
        return render(request, 'owner/colla.html', {'agents_data': agents_data})


class InternetplansView(LoginRequiredMixin, View):
    def get(self, request):
        form = InternetPlanForm()
        # Annotate each InternetPlan with the count of related Profiles
        plans = InternetPlan.objects.annotate(No_Users=Count('plan')).order_by('plan_name')
        return render(request, 'owner/intrplans.html', {'form': form, 'all_plans': plans})

    def post(self, request):
        form = InternetPlanForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Plan Added Successfully')
            # After successful save, re-fetch and annotate plans to include the newly added one
            plans = InternetPlan.objects.annotate(No_Users=Count('plan')).order_by('plan_name')
            return render(request, 'owner/intrplans.html', {'form': form, 'all_plans': plans})
        else:
            messages.error(request, 'Please correct the errors below.')
            # If form is invalid, still fetch and annotate all plans to display the table
            plans = InternetPlan.objects.annotate(No_Users=Count('plan')).order_by('plan_name')
            return render(request, 'owner/intrplans.html', {'form': form, 'all_plans': plans})

    
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
        updated_client = CustomUser.objects.filter(id=id).select_related(
            'profileuser__builing_id__Agent'
        ).first()
        return render(request, 'owner/partials/usrrow.html', {'client': [updated_client]})

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
                Q(profileuser__phone__icontains=query)
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