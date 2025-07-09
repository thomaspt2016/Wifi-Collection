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
from django.urls import path,reverse_lazy
from common import views
from django.contrib.auth import views as auth_views
app_name = 'common'

urlpatterns = [
    path('', views.Homeview.as_view(), name='home'),
    path('aboutus', views.AboutUsview.as_view(), name='aboutus'),
    path('pricing', views.PricingView.as_view(), name='pricing'),
    path('signup', views.SignupView.as_view(), name='signup'),
    path('login', views.LoginformView.as_view(), name='login'),
    path('contactus', views.ContactusView.as_view(), name='contactus'),
    path('verify',views.OtpVerificationView.as_view(),name='verify'),
    path('password_reset/',
         auth_views.PasswordResetView.as_view(
             template_name='common/forgotpassword.html', # <--- Points to your custom template
             email_template_name='common/password_reset_email.html', # Template for the email body
             subject_template_name='common/password_reset_subject.txt',
             success_url=reverse_lazy('common:password_reset_done') # <--- ADD THIS LINE
         ),
         name='password_reset'),
    path('password_reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='common/password_reset_done.html'
         ),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='common/password_reset_confirm.html',
             success_url=reverse_lazy('common:password_reset_complete') # <--- ADD THIS LINE
         ),
         name='password_reset_confirm'),
    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='common/password_reset_complete.html'
         ),
         name='password_reset_complete'),
    path('signout',views.SignoutView.as_view(),name='signout'),
]