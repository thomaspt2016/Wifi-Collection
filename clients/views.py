from django.shortcuts import get_object_or_404, render
from django.views import View
from django.shortcuts import render,redirect
from django.views import View
from django.http import HttpResponse, HttpResponseBadRequest
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from common import models
from .forms import TicketRasing,TicketReply
import os,datetime
import razorpay
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from common import utils
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.decorators import method_decorator

def Client_required(function):
    def wrap(request, *args, **kwargs):
        usr = models.CustomUser.objects.get(id=request.user.id)
        print(usr.role)
        if usr.role == 'client':
            return function(request, *args, **kwargs)
        else:
            return redirect(reverse('common:home'))
    return wrap

@method_decorator(Client_required, name='dispatch')
class ClientHomeView(LoginRequiredMixin,View):#this is where dashboard codes comes in
    def get(self,request):
        return redirect('common:home')


@method_decorator(Client_required, name='dispatch')
class WificodesView(LoginRequiredMixin, View):
    def get(self, request):
        usr = request.user
        billplan = models.BillingPlan.objects.filter(billingusr = usr,PlanStatus = 'Upcoming')
        codes = models.CodePoool.objects.filter(assignedto = usr,is_used = True,exiprydate__gt=datetime.datetime.now()).order_by('-exiprydate')
        return render(request, 'client/cliwificode.html',{'codeobject':codes,'billingplan':billplan})
    
@method_decorator(Client_required, name='dispatch')
class CurrentBillView(LoginRequiredMixin, View):
    def get(self, request):
        planobj = models.InternetPlan.objects.all()
        codecoutn = models.CodePoool.objects.filter(is_used = False).count()
        try:
            billplan = models.BillingPlan.objects.filter(billingusr = request.user, PlanStatus = 'Upcoming').first()
            return render(request, 'client/clibill.html',{'plan': planobj,'billplan':billplan,'codecount':codecoutn})
        except:
            return render(request, 'client/clibill.html',{'plan': planobj,'codecount':codecoutn})

    
@method_decorator(Client_required, name='dispatch')
class PaymenHistoryView(LoginRequiredMixin,View):
    def get(self, request):
        usr = request.user
        payhist = models.Payment.objects.filter(payment_user = usr)
        return render(request, 'client/payhist.html',{'paymenthist':payhist})

@method_decorator(Client_required, name='dispatch')
class RaiseTicketView(LoginRequiredMixin, View):
    def get(self, request):
        forminst = TicketRasing()
        reply_form = TicketReply()
        tickets = models.Ticketing.objects.filter(ticketraised=request.user).order_by('-ticketdate').prefetch_related(
            'updates__ticketupdateby',
            'ticketto',
            'ticketraised'         )
        for ticket in tickets:
            if ticket.ticketfile:
                ticket.ticketfile_basename = os.path.basename(ticket.ticketfile.name)
            else:
                ticket.ticketfile_basename = None

            for update in ticket.updates.all():
                if update.ticketupdatefile:
                    update.ticketupdatefile_basename = os.path.basename(update.ticketupdatefile.name)
                else:
                    update.ticketupdatefile_basename = None

        context = {
            'form': forminst,
            'tickets': tickets,
            'reply_form':reply_form
        }
        return render(request, 'client/ticket.html', context) # Make sure this template path is correct

    def post(self, request):
        usr = request.user
        forminst = TicketRasing(request.POST, request.FILES)

        if forminst.is_valid():
            ticket = forminst.save(commit=False)
            ticket.ticketraised = usr

            # Check for building_id and Agent properly
            if hasattr(usr, 'profileuser') and usr.profileuser.builing_id:
                if usr.profileuser.builing_id.Agent:
                    ticket.ticketto = usr.profileuser.builing_id.Agent
                    ticket.save()
                    messages.success(request, 'Ticket Raised Successfully!')
                    return redirect('clients:raise')
                else:
                    messages.error(request, 'The associated building does not have an assigned agent. Please contact support.')
                    tickets = models.Ticketing.objects.filter(ticketraised=request.user).order_by('-ticketdate').prefetch_related(
                        'updates__ticketupdateby',
                        'ticketto',
                        'ticketraised'
                    )
                    for tkt in tickets: # Need to process basenames again for the re-rendered page
                        if tkt.ticketfile:
                            tkt.ticketfile_basename = os.path.basename(tkt.ticketfile.name)
                        else:
                            tkt.ticketfile_basename = None
                        for upd in tkt.updates.all():
                            if upd.ticketupdatefile:
                                upd.ticketupdatefile_basename = os.path.basename(upd.ticketupdatefile.name)
                            else:
                                upd.ticketupdatefile_basename = None
                    return render(request, 'client/ticket.html', {'form': forminst, 'tickets': tickets})
            else:
                messages.error(request, 'Your profile is incomplete or not linked to a building. Please contact support.')
                # Re-render the form with errors and existing tickets
                tickets = models.Ticketing.objects.filter(ticketraised=request.user).order_by('-ticketdate').prefetch_related(
                    'updates__ticketupdateby',
                    'ticketto',
                    'ticketraised'
                )
                for tkt in tickets: # Need to process basenames again
                    if tkt.ticketfile:
                        tkt.ticketfile_basename = os.path.basename(tkt.ticketfile.name)
                    else:
                        tkt.ticketfile_basename = None
                    for upd in tkt.updates.all():
                        if upd.ticketupdatefile:
                            upd.ticketupdatefile_basename = os.path.basename(upd.ticketupdatefile.name)
                        else:
                            upd.ticketupdatefile_basename = None
                return render(request, 'client/ticket.html', {'form': forminst, 'tickets': tickets})
        else:
            messages.error(request, 'Please correct the errors below.')
            # Re-render the form with errors and existing tickets
            tickets = models.Ticketing.objects.filter(ticketraised=request.user).order_by('-ticketstatus').prefetch_related(
                'updates__ticketupdateby',
                'ticketto',
                'ticketraised'
            )
            for tkt in tickets: # Need to process basenames again
                if tkt.ticketfile:
                    tkt.ticketfile_basename = os.path.basename(tkt.ticketfile.name)
                else:
                    tkt.ticketfile_basename = None
                for upd in tkt.updates.all():
                    if upd.ticketupdatefile:
                        upd.ticketupdatefile_basename = os.path.basename(upd.ticketupdatefile.name)
                    else:
                        upd.ticketupdatefile_basename = None
            return render(request, 'client/ticket.html', {'form': forminst, 'tickets': tickets})

@method_decorator(Client_required, name='dispatch')
class TicketReplyView(LoginRequiredMixin, View):
    def post(self, request, ticket_id):
        ticket = models.Ticketing.objects.get(ticketid=ticket_id)
        reply_form = TicketReply(request.POST, request.FILES)
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
        return redirect('clients:raise')

@method_decorator(Client_required, name='dispatch')
class FAQView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'client/faq.html')
    
@method_decorator(Client_required, name='dispatch')
class OrderFormView(LoginRequiredMixin, View):
    def get(self, request,id):
        planobj = models.InternetPlan.objects.get(plan_id=id)
        prof = models.Profile.objects.get(user = request.user)
        try:
            if prof.plan.plan_name == planobj.plan_name:
                billing_action = 'Renew'
            elif prof.plan.plan_name > planobj.plan_name:
                billing_action = 'Upgrade'
            else:
                billing_action = 'Downgrade'
            return render(request, 'client/orderfor.html', {'plan': planobj,'billing_action': billing_action})
        except Exception as e:
            print(e)
            return render(request, 'client/orderfor.html', {'plan': planobj})
    def post(self, request, id):
        planobj = models.InternetPlan.objects.get(plan_id=id)
        usr = request.user
        Mode = request.POST.get('payment_method')
        print(request.POST)
        if Mode == 'cash':
                models.Payment.objects.create(
                payment_user = usr,
                payment_plan = planobj,
                payment_amount = planobj.plan_price,
                payment_method = 'Cash',
                payment_status = 'Pending'
            )
                return redirect('clients:cashsuc')
        if Mode == 'online':
                    try:
                        us = models.CustomUser.objects.get(username = usr)
                        clinent = razorpay.Client(auth=("rzp_test_cvS1Hu5zkwJQud", "uEj70mAqVU0IhlyYzHqfLznq"))
                        amountinpais = int(planobj.plan_price * 100)
                        payment = clinent.order.create({'amount': amountinpais, 'currency': 'INR', 'payment_capture': '1',
                                                        "partial_payment":False})
                        models.Payment.objects.create(
                            payment_user = usr,
                            payment_plan = planobj,
                            payment_amount = planobj.plan_price,
                            payment_method = 'Online',
                            payment_status = 'Pending',
                            online_payment_id = payment['id']
                        )
                        return render(request,'client/payment.html',{'payment':payment,'name':us})
                        
                    except Exception as e:
                        print(e)
                        messages.error(request, "Currently items not available")
                        return render(request, 'client/orderfor.html', {'plan': planobj})
                    
        return redirect('clients:cashsuc')

@method_decorator(Client_required, name='dispatch')
class CashSuccessView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'client/paycashsuc.html')




@method_decorator(csrf_exempt, name='dispatch')
class PaymentVerify(View):
    def post(self, request):
        print(request.POST)
        try:
            payment_id = request.POST.get('razorpay_payment_id')
            order_id = request.POST.get('razorpay_order_id')
            signature = request.POST.get('razorpay_signature')

            if not all([payment_id, order_id, signature]):
                return HttpResponseBadRequest("Missing required parameters")

            client = razorpay.Client(auth=("rzp_test_cvS1Hu5zkwJQud", "uEj70mAqVU0IhlyYzHqfLznq"))
            params_dict = {
                'razorpay_order_id': order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }
            client.utility.verify_payment_signature(params_dict)

            payment_details = client.payment.fetch(payment_id)
            print(payment_details)
            if payment_details['status'] != 'captured':
                return render(request, 'client/paymentf.html', {'error': 'Payment not captured.'})

            invoice = models.Payment.objects.get(online_payment_id=order_id)
            invoice.payment_status = 'Success'
            invoice.save()

            internet_plan = invoice.payment_plan
            billing_user = request.user
            
            codes_to_assign_count = internet_plan.Num_Devices
            
            # --- START OF FIX ---
            # 1. Select the IDs of the codes you want to update.
            # `values_list('id', flat=True)` retrieves a list of IDs efficiently.
            code_ids_to_update = list(models.CodePoool.objects.filter(is_used=False).values_list('codeid', flat=True)[:codes_to_assign_count])
            
            # 2. Define the data for the update.
            code_update_data = {
                'is_used': True,
                'assignedto': billing_user,
                'Invoice': invoice,
            }

            # 3. Add other data based on plan status.
            has_current_plan = models.BillingPlan.objects.filter(billingusr=billing_user, PlanStatus='Current').exists()
            has_upcoming_plan = models.BillingPlan.objects.filter(billingusr=billing_user, PlanStatus='Upcoming').exists()

            if has_current_plan or has_upcoming_plan:
                billing_status = 'Upcoming'
                code_remarks = 'Upcoming'
                start_date = None
                end_date = None
            else:
                billing_status = 'Current'
                code_remarks = 'Active'
                start_date = datetime.date.today()
                end_date = start_date + datetime.timedelta(days=30)
                
                models.Profile.objects.filter(user=billing_user).update(plan=internet_plan)
                
                code_update_data.update({
                    'assigneddate': datetime.datetime.now(),
                    'exiprydate': datetime.datetime.now() + datetime.timedelta(days=180),
                })
            
            code_update_data['remarks'] = code_remarks
            
            # 4. Perform the update using the list of IDs.
            # The `id__in` filter creates an unsliced queryset, which can be updated.
            models.CodePoool.objects.filter(codeid__in=code_ids_to_update).update(**code_update_data)
            # --- END OF FIX ---
            
            billing = models.BillingPlan.objects.create(
                paymentid=invoice,
                billingusr=billing_user,
                billingplan=internet_plan,
                PlanStatus=billing_status,
                billstartdate=start_date,
                billendate=end_date
            )
            
            assigned_codes = models.CodePoool.objects.filter(assignedto=billing_user, Invoice=invoice)
            utils.send_payment_success_email(
                billing_user,
                invoice.InvoiceId,
                invoice.online_payment_id,
                internet_plan.plan_name,
                assigned_codes,
                billing.billstartdate,
                billing.billendate
            )

            return render(request, 'client/paysucesin.html')

        except razorpay.errors.SignatureVerificationError as e:
            print(f"Signature verification failed: {e}")
            return render(request, 'client/paymentf.html', {'error': 'Invalid payment signature.'})

        except razorpay.errors.BadRequestError as e:
            print(f"Razorpay API error: {e}")
            return render(request, 'client/paymentf.html', {'error': f'Razorpay API Error: {e}'})

        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            try:
                invoice = models.Payment.objects.get(online_payment_id=order_id)
                invoice.payment_status = 'Failed'
                invoice.save()
            except models.Payment.DoesNotExist:
                pass 
            return render(request, 'client/paymentf.html', {'error': f'An unexpected error occurred: {e}'})


@method_decorator(Client_required, name='dispatch')
class PayCancel(View):
    def get(self, request,i):
        try:
            payment_obj = get_object_or_404(models.Payment, online_payment_id=i)
            payment_obj.payment_status = 'Failed'
            payment_obj.save() # Save the changes to the database
            print(f"Payment {i} status updated to Failed (cancelled).")
            return render(request, 'client/paymentf.html', {"error":f"Payment {i} status updated to Failed (cancelled)."})

        except Exception as e:
            print(f"Error updating payment {i} status to Failed: {e}")
            return render(request, 'client/paymentf.html',{"error":e})

@method_decorator(Client_required, name='dispatch')
class TicketClose(View):
    def post(self, request, ticket_id):
        ticket = models.Ticketing.objects.get(ticketid=ticket_id)
        ticket.ticketstatus = 'Closed'
        ticket.save()
        return redirect('clients:raise')