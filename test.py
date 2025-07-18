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