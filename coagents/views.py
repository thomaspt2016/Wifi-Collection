from django.shortcuts import render
from django.views import View
from django.shortcuts import render,redirect
from django.views import View
from django.http import HttpResponse
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from common import models
from django.db.models import Q,Sum
from django.db.models import Exists, OuterRef
from common import utils
import datetime
from clients import forms
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.decorators import method_decorator

def Co_Agent_required(function):
    def wrap(request, *args, **kwargs):
        usr = models.CustomUser.objects.get(id=request.user.id)
        print(usr.role)
        if usr.role == 'coagent':
            return function(request, *args, **kwargs)
        else:
            return redirect(reverse('common:home'))
    return wrap

@method_decorator(Co_Agent_required, name='dispatch')
class CoHomeView(LoginRequiredMixin,View):
    def get(self,request):
        return redirect('common:home')
    
@method_decorator(Co_Agent_required, name='dispatch')
class CoClientsView(LoginRequiredMixin,View):
    def get(self, request):
        customuser_fields = [
            'id', 'first_name', 'last_name', 'email', 'is_active',
        ]
        profileuser_fields = [
            'profileuser__profpic', 
            'profileuser__builing_id', # Note the corrected field name here
            'profileuser__floor',
            'profileuser__room',
            'profileuser__phone',
        ]
        building_fields = [
            'profileuser__builing_id__Agent__first_name', 
            'profileuser__builing_id__Agent__last_name', 
        ]

        clients = models.CustomUser.objects.filter(
            role='client',
            profileuser__builing_id__Agent=request.user
        ).select_related(
            'profileuser__builing_id__Agent'
        ).only(
            *customuser_fields,
            *profileuser_fields,
            *building_fields
        ).order_by('last_name', 'first_name')

        # --- Pagination Logic ---
        paginator = Paginator(clients, 10)

        page_number = request.GET.get('page')
        try:
            clients = paginator.page(page_number)
        except PageNotAnInteger:
            clients = paginator.page(1)
        except EmptyPage:
            clients = paginator.page(paginator.num_pages)
        # --- End Pagination Logic ---

        return render(request, 'coagent/coclients.html', {'client': clients})

@method_decorator(Co_Agent_required, name='dispatch')
class SearchUserView(LoginRequiredMixin, View):
    def get(self, request):
        query = request.GET.get('q', '').strip()
        print(query)
        page_number = request.GET.get('page', 1)

        clients_qs = models.CustomUser.objects.filter(
            role='client',
            profileuser__builing_id__Agent=request.user
        ).select_related(
            'profileuser',
            'profileuser__builing_id',
            'profileuser__builing_id__Agent'
        ).order_by('last_name', 'first_name')

        if query:
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
        return render(request, 'coagent/partials/usrrow.html', {'client': clients})


@method_decorator(Co_Agent_required, name='dispatch')
class DueViews(LoginRequiredMixin, View):
    def get(self, request):
        print("in dues")
        upcoming_plan_exists_subquery = models.BillingPlan.objects.filter(
            billingusr=OuterRef('payment_user'),
            PlanStatus='Upcoming'
        )

        pendingpay = models.Payment.objects.filter(
            payment_status='Pending',
            payment_user__profileuser__builing_id__Agent=request.user
        ).annotate(
            has_upcoming_plan=Exists(upcoming_plan_exists_subquery)
        ).select_related(
            'payment_user',
            'payment_user__profileuser',
            'payment_user__profileuser__builing_id',
            'payment_user__profileuser__builing_id__Agent'
        ).order_by('payment_user__last_name', 'payment_user__first_name')
        
        return render(request, 'coagent/due.html',{'duepay': pendingpay})
    
@method_decorator(Co_Agent_required, name='dispatch')
class ProfiledetailView(LoginRequiredMixin, View):
    def get(self, request,id):
        try:
            profile = models.Profile.objects.select_related(
                                    'user',   # Fetches the CustomUser object
                                    'plan'    # Fetches the InternetPlan object
                                    ).filter(user__profileuser__builing_id__Agent=request.user).prefetch_related(
                                        'user__paymentsusr',          # Fetches all related Payment objects
                                        'user__billingusr',           # Fetches all related BillingPlan objects
                                        'user__assigned_codes',       # Fetches all related CodePoool objects
                                        'user__uploaded_wifi_codes'   # Fetches all related WifiCodeUpload objects
                                    ).order_by('user__assigned_remarks').get(user=id)
            PaymentMethodSummary = models.Payment.objects.filter(
                    payment_user=id,
                    payment_status='Success'
                ).values(
                    'payment_method'  # Group the payments by their method
                ).annotate(
                    total_amount=Sum('payment_amount')  # Calculate the sum for each group
                )

            return render(request, 'coagent/profile.html', {'profile': profile,'paymentmeth':PaymentMethodSummary})    
        except:
            return redirect('coagents:coclients')
        
@method_decorator(Co_Agent_required, name='dispatch')
class AcountDisable(LoginRequiredMixin,View):
    def post(self,request,id):
        us = models.CustomUser.objects.get(id = id)
        if 'is_active' in request.POST:
            us.is_active = True
        else:
            us.is_active = False
        us.save()
        clients = models.CustomUser.objects.filter(role='client').select_related(
            'profileuser',                      
            'profileuser__builing_id',
            'profileuser__builing_id__Agent'
        )
        updated_client = models.CustomUser.objects.filter(id=id).select_related(
            'profileuser__builing_id__Agent'
        ).first()
        return render(request, 'coagent/partials/usrrow.html', {'client': [updated_client]})

@method_decorator(Co_Agent_required, name='dispatch')
class CashPaymentDelete(LoginRequiredMixin, View):
    def post(self, request, id):
        payobj=models.Payment.objects.get(InvoiceId=id)
        payobj.payment_status = "Failed"
        payobj.save()
        return redirect('coagents:DueView')

@method_decorator(Co_Agent_required, name='dispatch')
class CashPaymentSuccess(LoginRequiredMixin, View):
    def post(self, request, id):
        """
        This view processes a cash payment confirmation.
        
        It updates the payment status to 'Success' and then creates
        a new BillingPlan for the client associated with the payment.
        
        Args:
            request: The Django request object.
            id: The InvoiceId of the payment to be processed.
        """
        
        try:
            # 1. Fetch the payment object and related data once for efficiency
            payobj = models.Payment.objects.select_related('payment_user', 'payment_plan').get(InvoiceId=id)
            
            # The client whose payment is being processed
            client_user = payobj.payment_user
            
            # The plan associated with this payment
            paid_plan = payobj.payment_plan

            # 2. Update the payment status to "Success"
            payobj.payment_status = "Success"
            payobj.save()

            # Initialize date variables to ensure they are always defined
            new_plan_start_date = None
            new_plan_end_date = None
            
            # Initialize remarks variable
            code_remarks = 'Unknown'

            # 3. Check for the client's current plan status to determine the new plan's status and dates.
            current_plan = models.BillingPlan.objects.filter(
                billingusr=client_user, 
                PlanStatus='Current'
            ).first()

            if current_plan:
                # If a 'Current' plan exists, the new plan is 'Upcoming'
                # and starts after the current plan ends.
                new_plan_start_date = current_plan.billendate + datetime.timedelta(days=1)
                new_plan_end_date = new_plan_start_date + datetime.timedelta(days=paid_plan.Duration)
                new_plan_status = 'Upcoming'
                code_remarks = 'Upcoming'
            else:
                # If no 'Current' plan exists, the new plan is 'Current'
                # and starts today.
                new_plan_start_date = datetime.date.today()
                new_plan_end_date = new_plan_start_date + datetime.timedelta(days=paid_plan.Duration)
                new_plan_status = 'Current'
                code_remarks = 'Active'

            # 4. Create the new BillingPlan record using the dates and status determined above.
            billing_plan = models.BillingPlan.objects.create(
                paymentid=payobj,
                billingusr=client_user,
                billingplan=paid_plan,
                billstartdate=new_plan_start_date,
                billendate=new_plan_end_date,
                PlanStatus=new_plan_status
            )
            
            # 5. Update the client's profile with the new plan only if it's 'Current'
            if new_plan_status == 'Current':
                models.Profile.objects.filter(user=client_user).update(plan=paid_plan)

            # 6. Assign available WiFi codes to the client. This logic runs once.
            num_devices = paid_plan.Num_Devices
            
            # Get the IDs of the required number of unused codes
            codes_to_assign_ids = models.CodePoool.objects.filter(
                is_used=False
            ).values_list('codeid', flat=True)[:num_devices]

            # Update the selected codes in a single query
            models.CodePoool.objects.filter(codeid__in=codes_to_assign_ids).update(
                is_used=True,
                assignedto=client_user,
                assigneddate=datetime.datetime.now(),
                exiprydate=datetime.datetime.now() + datetime.timedelta(days=paid_plan.Duration),
                Invoice=payobj,
                remarks=code_remarks # Use the dynamic remarks value here
            )
            
            # 7. Fetch the newly assigned codes for the email.
            assigned_codes = models.CodePoool.objects.filter(
                assignedto=client_user,
                Invoice=payobj
            )

            # 8. Send the success email to the client.
            utils.send_payment_success_email(
                client_user,
                payobj.InvoiceId,
                payobj.online_payment_id,
                paid_plan.plan_name,
                assigned_codes,
                billing_plan.billstartdate,
                billing_plan.billendate
            )
            return render(request, 'coagent/due.html')

        except models.Payment.DoesNotExist:
            return redirect('DueView')
        
@method_decorator(Co_Agent_required, name='dispatch')
class Ticketview(LoginRequiredMixin, View):
    def get(self, request):
        teplyform = forms.TicketReply()
        tickets = models.Ticketing.objects.filter(
            ticketto=request.user
        ).prefetch_related('updates').order_by('-ticketdate')

        return render(request, 'coagent/tickets.html', {'tickets': tickets,'reply_form':teplyform})
    
@method_decorator(Co_Agent_required, name='dispatch')
class TicketReplyView(LoginRequiredMixin, View):
    def post(self, request, ticket_id):
        ticket = models.Ticketing.objects.get(ticketid=ticket_id)
        reply_form = forms.TicketReply(request.POST, request.FILES)
        if reply_form.is_valid():
            reply = reply_form.save(commit=False)
            reply.ticketupdateby = request.user
            reply.ticketid = ticket
            ticket.ticketstatus = 'In Progress'
            ticket.save()
            reply.save()
            messages.success(request, 'Reply sent successfully!')
        else:
            messages.error(request, 'Please correct the errors below.')
        return redirect('coagents:ticketview')

@method_decorator(Co_Agent_required, name='dispatch')
class TicketClose(View):
    def post(self, request, ticket_id):
        ticket = models.Ticketing.objects.get(ticketid=ticket_id)
        ticket.ticketstatus = 'Closed'
        ticket.save()
        return redirect('coagents:ticketview')