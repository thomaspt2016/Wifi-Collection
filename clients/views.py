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
from .forms import TicketRasing

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
        forminst = TicketRasing()
        tickets = models.Ticketing.objects.filter(ticketraised=request.user
                                                  ).prefetch_related(
                                                      'updates'
                                                  )
        return render(request, 'client/ticket.html',{'form':forminst,'tickets':tickets})

    def post(self, request):
        usr = request.user
        forminst = TicketRasing(request.POST, request.FILES)
        if forminst.is_valid():
            ticket = forminst.save(commit=False)
            ticket.ticketraised = usr
            if hasattr(usr, 'profileuser') and usr.profileuser.builing_id:
                if usr.profileuser.builing_id.Agent:
                    ticket.ticketto = usr.profileuser.builing_id.Agent
                    ticket.save()
                    messages.success(request, 'Ticket Raised Successfully!')
                    return redirect('clients:raise')
                else:
                    messages.error(request, 'The associated building does not have an assigned agent. Please contact support.')
                    return render(request, 'client/ticket.html', {'form': forminst})
            else:
                messages.error(request, 'Your profile is incomplete or not linked to a building. Please contact support.')
                return render(request, 'client/ticket.html', {'form': forminst})
        else:
            messages.error(request, 'Please correct the errors below.')
            return render(request, 'client/ticket.html', {'form': forminst})

class FAQView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'client/faq.html')

class ContactAgentView(LoginRequiredMixin,View):
    def get(self,request):
        return render(request, 'client/agent.html')