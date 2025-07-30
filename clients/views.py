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
from .forms import TicketRasing,TicketReply
import os

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
