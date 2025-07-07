from django.views import View
from .forms import SignupForm
from django.shortcuts import render,redirect
from django.views import View
from django.http import HttpResponse
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.auth import authenticate,login,logout

# Create your views here.

class Homeview(View):
    def get(self,request):
        return render(request, 'common/home.html')

class AboutUsview(View):
    def get(self,request):
        return render(request, 'common/aboutus.html')

class PricingView(View):
    def get(self, request):
        return render(request, 'common/pricing.html')

class SignupView(View):
    def get(self, request):
        form_instance = SignupForm(request.POST)
        return render(request, 'common/sighnup.html',{'form':form_instance})
    
    def post(self, request):
        form_instance = SignupForm(request.POST)
        if form_instance.is_valid():
            print("form is valid")
            user=form_instance.save(commit=False)
            user.is_active=False
            user.save()
            user.generate_otp()
            send_mail(
                'OTP Test',
                user.otp,
                'thomaspt2016@example.com',
                [user.email],
                fail_silently=False,
                )
            return redirect('loginfo:verifyotp')
        else:
            print("form is not valid")
            return render(request, 'login/signup.html', {'form': form_instance})

class LoginformView(View):
    def get(self, request):
        return render(request, 'common/login.html')

class ContactusView(View):
    def get(self, request):
        return render(request, 'common/contactus.html')