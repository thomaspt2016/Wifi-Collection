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
app_name = 'coagents'

urlpatterns = [
    path('cohome',views.CoHomeView.as_view(),name='cohome'),
    path('coclients', views.CoClientsView.as_view(), name='coclients'),
    path('searchuser', views.SearchUserView.as_view(), name='searchuser'),
    path('dues',views.DueViews.as_view(),name='DueView'),
    path('profiledetails/<int:id>',views.ProfiledetailView.as_view(),name='profiledetails'),
    path('activecheck/<int:id>', views.AcountDisable.as_view(), name='activecheck'),
    path('paymentsucs/<str:id>', views.CashPaymentSuccess.as_view(), name='paymentsucs'),
    path('paymentsdel/<str:id>', views.CashPaymentDelete.as_view(), name='paymentsdel'),
]
