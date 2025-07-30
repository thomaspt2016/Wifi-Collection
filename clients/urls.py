"""
URL configuration for wificollection project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views
app_name = 'clients'

urlpatterns = [
    path('clienthome',views.ClientHomeView.as_view(),name='clienthome'),
    path('cliwificode', views.WificodesView.as_view(), name='cliwificode'),
    path('clibill', views.CurrentBillView.as_view(), name='clibill'),
    path('payhist', views.PaymenHistoryView.as_view(), name='payhist'),
    path('raise', views.RaiseTicketView.as_view(), name='raise'),
    path('faq', views.FAQView.as_view(), name='faq'),
    path('replay/<int:ticket_id>', views.TicketReplyView.as_view(), name='replay')
]
