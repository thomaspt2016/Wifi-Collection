from django.shortcuts import get_object_or_404, render
from django.views import View
from django.shortcuts import render,redirect
from django.views import View
from django.http import HttpResponse, HttpResponseBadRequest
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.mixins import LoginRequiredMixin
from common import models
from .forms import TicketRasing,TicketReply
import os,datetime
import razorpay
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt



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
        return render(request, 'client/clibill.html',{'plan': planobj})
    
class PaymenHistoryView(LoginRequiredMixin,View):
    def get(self, request):
        usr = request.user
        payhist = models.Payment.objects.filter(payment_user = usr)
        return render(request, 'client/payhist.html',{'paymenthist':payhist})

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

class FAQView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'client/faq.html')
    
class OrderFormView(LoginRequiredMixin, View):
    def get(self, request,id):
        planobj = models.InternetPlan.objects.get(plan_id=id)
        prof = models.Profile.objects.get(user = request.user)
        if prof.plan.plan_name == planobj.plan_name:
            billing_action = 'Renew'
        elif prof.plan.plan_name > planobj.plan_name:
            billing_action = 'Downgrade'
        else:
            billing_action = 'Upgrade'
        return render(request, 'client/orderfor.html', {'plan': planobj,'billing_action': billing_action})
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
                    print("online")
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

        

class CashSuccessView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'client/paycashsuc.html')

@method_decorator(csrf_exempt, name='dispatch')
class PaymentVerify(View):
    def post(self,request):
        print(request.POST)
        try:
            paymenid = request.POST.get('razorpay_payment_id',' ')
            orderid = request.POST.get('razorpay_order_id',' ')
            signature = request.POST.get('razorpay_signature',' ')
            if not all([paymenid, orderid, signature]):
                return HttpResponseBadRequest("Missing required parameters")
            params = {
                'razorpay_order_id': orderid,
                'razorpay_payment_id': paymenid,
                'razorpay_signature': signature
            }
            clinent = razorpay.Client(auth=("rzp_test_cvS1Hu5zkwJQud", "uEj70mAqVU0IhlyYzHqfLznq"))
            clinent.utility.verify_payment_signature(params)
            payment = clinent.payment.fetch(paymenid)
            print(payment)
            if payment['status'] == 'captured':
                billing = models.BillingPlan.objects.create(
                    paymentid = models.Payment.objects.get(online_payment_id = orderid),
                    billingusr = request.user,
                    billingplan = models.InternetPlan.objects.get(plan_id = models.Payment.objects.get(online_payment_id = orderid
                                                                                                       ).payment_plan.plan_id),
                    )
                if models.BillingPlan.objects.filter(billingusr = request.user, PlanStatus = 'Upcoming').exists():
                    billing.PlanStatus = 'Upcoming'
                    billing.save()
                else:
                    billing.PlanStatus = 'Current'
                    billing.billstartdate = datetime.date.today()
                    billing.billendate = datetime.date.today() + datetime.timedelta(days=30)
                    billing.save()
                payment = models.Payment.objects.get(online_payment_id = orderid)
                payment.payment_status = 'Success'
                payment.save()
                return render(request, 'client/paysucesin.html')
            else:
                payment = models.Payment.objects.get(online_payment_id = orderid)
                payment.payment_status = 'Failed'
                payment.save()
                return render(request, 'client/paymentf.html')
        except razorpay.errors.SignatureVerificationError as e:
            print(f"Signature verification failed: {e}")
            return render(request, 'client/payment_failure.html', {'error': 'Payment verification failed: Invalid signature.'})
        except razorpay.errors.BadRequestError as e:
            # Handle other Razorpay API errors (e.g., payment_id not found)
            print(f"Razorpay API error: {e}")
            return render(request, 'client/payment_failure.html', {'error': f'Razorpay API Error: {e}'})
        except Exception as e:
            # Catch any other unexpected errors
            print(f"An unexpected error occurred: {e}")
            return render(request, 'client/payment_failure.html', {'error': f'An unexpected error occurred: {e}'})
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

class TicketClose(View):
    def post(self, request, ticket_id):
        ticket = models.Ticketing.objects.get(ticketid=ticket_id)
        ticket.ticketstatus = 'Closed'
        ticket.save()
        return redirect('clients:raise')