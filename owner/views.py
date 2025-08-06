from django.shortcuts import render
from django.views import View
from django.shortcuts import render,redirect
from django.views import View
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from common.models import CustomUser,InternetPlan,CodePoool,WifiCodeUpload,Profile,Payment,Building,Ticketing,TicketUpdates
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q,Count
from common.forms import InternetPlanForm
import PyPDF2
import re
import os
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
import datetime
from django.db.models import Q,Sum


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
        agents_data = []
        unique_building_names = Building.objects.values_list('building_name', flat=True).distinct()
        allbul = list(unique_building_names)

        for agent in collection_agents:
            # Get the list of building names for the current agent
            unique_building_names = list(agent.buildings_managed.all().values_list('building_name', flat=True).distinct())
            
            agents_data.append({
                'agent': agent,
                'unique_buildings': unique_building_names,
            })
        
        context = {
            'agents_data': agents_data,
            'all_buildings': allbul,
        }

        return render(request, 'owner/colla.html', context)

class SearchViewPool(LoginRequiredMixin,View):
    def post(self, request):
        search_query = request.POST.get('search_query', '').strip()
        if search_query:
            clintls= CustomUser.objects.exclude(role='owner').select_related(
                'profileuser',
                'profileuser__plan'
            )
        else:
            search_results = []
        return render(request, 'owner/search_results.html', {'search_results': search_results})
    


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
        ta = WifiCodeUpload.objects.all()
        if ta:
            ta = ta.order_by('-uploadeddate')
            return render(request, 'owner/codup.html',{'codeuploaddata': ta})
        else:
            return render(request, 'owner/codup.html')
    
    def post(self, request):
        if 'codefile' not in request.FILES:
            messages.error(request, 'No file was uploaded.')
            codeuploaddata = WifiCodeUpload.objects.all().order_by('-uploadeddate')
            return render(request, 'owner/codup.html', {'codeuploaddata': codeuploaddata})

        uploaded_file = request.FILES['codefile']
        remarks = request.POST.get('remarks', "Havent Provided any remarks")

        wifi_code_upload_instance = None
        file_absolute_path_for_pypdf = None

        try:
            wifi_code_upload_instance = WifiCodeUpload.objects.create(
                uploadstatus="Processing",
                uploadedby=request.user,
                uploadedto=uploaded_file,
                remarks=remarks
            )

            file_absolute_path_for_pypdf = wifi_code_upload_instance.uploadedto.path

            pdf_content = self.read_pdf_pypdf2(file_absolute_path_for_pypdf)
            pattern = r'\b6may\d{6}\b'
            codes = re.findall(pattern, pdf_content)

            new_codes_count = 0
            duplicate_codes_count = 0
            found_duplicates = False # Flag to track if any duplicates were found

            if codes:
                for code_str in codes:
                    try:
                        CodePoool.objects.get(code=code_str)
                        messages.error(request, f'Code {code_str} already exists in the database.')
                        duplicate_codes_count += 1
                        found_duplicates = True
                    except CodePoool.DoesNotExist:
                        CodePoool.objects.create(
                            code=code_str,
                            sourcepdf=wifi_code_upload_instance
                        )
                        new_codes_count += 1
                
                # Determine upload status based on duplicate findings
                if found_duplicates and new_codes_count > 0:
                    upload_status_db = 'Completed (with Duplicates)'
                    messages.warning(request, f'File uploaded. {new_codes_count} new codes saved, {duplicate_codes_count} codes already existed.')
                elif found_duplicates and new_codes_count == 0:
                    upload_status_db = 'All Codes Existed'
                    messages.warning(request, f'File uploaded. All {duplicate_codes_count} codes already existed and none were added.')
                else: # No duplicates, all codes were new
                    upload_status_db = 'Completed'
                    messages.success(request, f'File uploaded and {len(codes)} new codes extracted and saved successfully.')
            else:
                upload_status_db = 'No Codes Found'
                messages.warning(request, 'File uploaded, but no matching codes were found.')

            wifi_code_upload_instance.uploadstatus = upload_status_db
            wifi_code_upload_instance.save()

        except PyPDF2.errors.PdfReadError:
            upload_status_db = 'PDF Error'
            error_remarks = 'The uploaded file is not a valid PDF or is corrupted.'
            messages.error(request, error_remarks)
            if wifi_code_upload_instance:
                wifi_code_upload_instance.uploadstatus = upload_status_db
                wifi_code_upload_instance.remarks = error_remarks
                wifi_code_upload_instance.save()
            else:
                WifiCodeUpload.objects.create(
                    uploadstatus=upload_status_db,
                    uploadedby=request.user,
                    remarks=error_remarks
                )

        except Exception as e:
            upload_status_db = 'Processing Error'
            error_remarks = f'An unexpected error occurred during PDF processing: {e}'
            messages.error(request, error_remarks)
            if wifi_code_upload_instance:
                wifi_code_upload_instance.uploadstatus = upload_status_db
                wifi_code_upload_instance.remarks = error_remarks
                wifi_code_upload_instance.save()
            else:
                WifiCodeUpload.objects.create(
                    uploadstatus=upload_status_db,
                    uploadedby=request.user,
                    remarks=error_remarks
                )
        finally:
            pass

        codeuploaddata = WifiCodeUpload.objects.all().order_by('-uploadeddate')
        return render(request, 'owner/codup.html', {'codeuploaddata': codeuploaddata})

    def read_pdf_pypdf2(self, filepath):
        text = ""
        with open(filepath, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page_num in range(len(reader.pages)):
                text += reader.pages[page_num].extract_text()
        return text


@login_required(login_url='common:login')
def download_file_view(request, upload_id):
    try:
        upload_instance = get_object_or_404(WifiCodeUpload, codeupid=upload_id)
        file_path = upload_instance.uploadedto.path
    except Http404:
        messages.error(request, 'File not found.')
        return redirect('code_upload_url_name')

    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/pdf")
            response['Content-Disposition'] = 'attachment; filename="%s"' % os.path.basename(file_path)
            return response
    raise Http404
    
class CodePoolStatView(LoginRequiredMixin,View):
    def get(self,request):
        codepool_data = CodePoool.objects.all().exclude(remarks__in=['De-activated', 'Expired']).select_related('assignedto', 
                                                                'sourcepdf','assignedto__profileuser__plan'
                                                                ).all().order_by('assignedto')
        usr = CodePoool.objects.filter(assignedto__isnull=False).values('assignedto').distinct().count()
        activcodes = CodePoool.objects.filter(is_used=True, is_deactivated=False).count()
        totalcodes = CodePoool.objects.all().count()

        plan_code_counts = InternetPlan.objects.annotate(
            assigned_code_count=Count(
                'plan__user__assigned_codes',
                filter=Q(
                    plan__user__assigned_codes__is_used=True,
                    plan__user__assigned_codes__is_deactivated=False
                ),
                distinct=True
            )
        ).order_by('plan_name')
        items_per_page = 10
        paginator = Paginator(codepool_data, items_per_page)

        page_number = request.GET.get('page')
        try:
            codepool_data_paginated = paginator.page(page_number) # Get the Page object
        except PageNotAnInteger:
            codepool_data_paginated = paginator.page(1)
        except EmptyPage:
            codepool_data_paginated = paginator.page(paginator.num_pages)
        context = {
            'codepool_data': codepool_data_paginated, # Pass the paginated data
            'distinct_users_count': usr,
            'active_codes_count': activcodes,
            'total_used_codes_count': totalcodes,
            'plan_counts': plan_code_counts,
        }
        return render(request, 'owner/codepoo.html', context)

class SearchViewCodes(LoginRequiredMixin,View):
    def get(self, request):
        search_query = request.GET.get('q', '').strip() 
        clients_qs = CodePoool.objects.filter(is_used=True,is_deactivated=False
                                                  ).select_related(
            'assignedto', 
            'sourcepdf',
            'assignedto__profileuser__plan'
        ).all().order_by('assignedto')

        if search_query:
            # Corrected Q object filters
            clients_qs = clients_qs.filter(
                Q(assignedto__first_name__icontains=search_query) |
                Q(assignedto__email__icontains=search_query) |
                Q(assignedto__profileuser__phone__icontains=search_query) |
                Q(assignedto__profileuser__plan__plan_name__icontains=search_query) |
                Q(code__icontains=search_query)
            )
        
        context = {
            'codepool_data': clients_qs # Pass the filtered queryset to the template
        }
        return render(request, 'owner/partials/coderow.html', context)
   
class CodeDeactivation(LoginRequiredMixin,View):
    def post(self, request, invid):
        codes_to_deactivate = CodePoool.objects.filter(Invoice=invid, is_deactivated=False)

        if not codes_to_deactivate.exists():
            clients = CodePoool.objects.filter(is_used=True, is_deactivated=False).select_related('assignedto', 'sourcepdf', 'assignedto__profileuser__plan').all().order_by('assignedto')
            return render(request, 'owner/partials/coderow.html', {'codepool_data': clients})

        user_to_deactivate_codes_for = codes_to_deactivate.first().assignedto
        
        codes_to_deactivate.update(is_deactivated=True, deactivated=datetime.datetime.today(),remarks = 'De-activated')

        Profile.objects.filter(user=user_to_deactivate_codes_for).update(
            plan=None
        )

        clients = CodePoool.objects.filter(is_used=True, is_deactivated=False).select_related('assignedto', 'sourcepdf', 'assignedto__profileuser__plan').all().order_by('assignedto')

        return render(request, 'owner/partials/coderow.html', {'codepool_data': clients})
    

class PaymentsView(LoginRequiredMixin,View):
    def get(self, request):
        payments = Payment.objects.filter(payment_status='Success').order_by('-payment_date')
        Fpayments = Payment.objects.filter(payment_status ='Failed').order_by('-payment_date')
        Cashpayments = Payment.objects.filter(payment_method ='Cash',payment_status='Success').order_by('-payment_date')
        Onlinepayments = Payment.objects.filter(payment_method ='Online',payment_status='Success').order_by('-payment_date')
        PendinPayments = Payment.objects.filter(payment_status ='Pending').order_by('-payment_date')


        
        # Calculate the sum of payments grouped by payment method
        payment_methods_success = Payment.objects.filter(
            payment_status='Success'
        ).values('payment_method').annotate(
            total_amount=Sum('payment_amount')
        )

        # Calculate the sum of payments grouped by collection agent.
        # The lookup path has been corrected to traverse the models correctly:
        # Payment -> CustomUser (via payment_user) -> Profile (via profileuser related_name) ->
        # Building (via builing_id) -> CustomUser (via Agent)
        payments_by_agent = Payment.objects.filter(
            payment_status='Success'
        ).values(
            'payment_user__profileuser__builing_id__Agent__first_name',
            'payment_user__profileuser__builing_id__Agent__last_name'
        ).annotate(
            total_amount=Sum('payment_amount')
        ).order_by('payment_user__profileuser__builing_id__Agent')

        # Create a context dictionary to pass the data to the template
        context = {
            'payments': payments,
            'payment_methods_success': payment_methods_success,
            'payments_by_agent': payments_by_agent,
            'Fpayments':Fpayments,
            'Cashpayments':Cashpayments,
            'Onlinepayments':Onlinepayments,
            'PendinPayments':PendinPayments
        }
        return render(request, 'owner/payments.html', context)
    


class AcountDisable(LoginRequiredMixin,View):
    def post(self,request,id):
        us = CustomUser.objects.get(id = id)
        if 'is_active' in request.POST:
            us.is_active = True
        else:
            us.is_active = False
        us.save()
        clients = CustomUser.objects.filter(role='client').select_related(
            'profileuser',                      
            'profileuser__builing_id',
            'profileuser__builing_id__Agent'
        )
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
class UserPromotions(LoginRequiredMixin, View):
    def get(self, request,id):
        user = get_object_or_404(CustomUser, pk=id)
        prof = Profile.objects.get(user=user)

        if user.role=="client":
            user.role = "coagent"
            prof.is_billable = False
            prof.next_billdate = None
            prof.planenddate = None
        elif user.role=="coagent":
            user.role = "client"
        user.save()
        prof.save()

        return redirect('owner:ownclients')

class ProfiledetailView(LoginRequiredMixin, View):
    def get(self, request,id):
        try:
            profile = Profile.objects.select_related(
                                    'user',   # Fetches the CustomUser object
                                    'plan'    # Fetches the InternetPlan object
                                    ).prefetch_related(
                                        'user__paymentsusr',          # Fetches all related Payment objects
                                        'user__billingusr',           # Fetches all related BillingPlan objects
                                        'user__assigned_codes',       # Fetches all related CodePoool objects
                                        'user__uploaded_wifi_codes'   # Fetches all related WifiCodeUpload objects
                                    ).order_by('user__assigned_remarks').get(user=id)
            PaymentMethodSummary = Payment.objects.filter(
                    payment_user=id,
                    payment_status='Success'
                ).values(
                    'payment_method'  # Group the payments by their method
                ).annotate(
                    total_amount=Sum('payment_amount')  # Calculate the sum for each group
                )

            return render(request, 'owner/profile.html', {'profile': profile,'paymentmeth':PaymentMethodSummary})    
        except:
            return redirect('owner:ownclients')

class update_agent_buildings(LoginRequiredMixin, View):
    def post(self, request, id):
        try:
            print(id)
            agent = CustomUser.objects.get(id=id)
            Building.objects.filter(Agent=agent).update(Agent=None)
            buldinnlst = request.POST.getlist('buildings')
            for name in buldinnlst:
                Building.objects.filter(building_name=name).update(Agent=agent)
            return redirect('owner:collectionagents')
        except:
            return redirect('owner:collectionagents')


class TicketView(LoginRequiredMixin, View):
    def get(self, request):
        ticketdetails = Ticketing.objects.all().prefetch_related('updates').order_by('-ticketdate')
        return render(request, 'owner/tickets.html', {'ticketdetails': ticketdetails})