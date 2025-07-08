from django.views import View
from .forms import SignupForm
from django.shortcuts import render,redirect
from django.views import View
from django.http import HttpResponse
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.auth import authenticate,login,logout
from .models import CustomUser

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
            otp = user.generate_otp()
            send_mail(
                'OTP Test',
                otp,
                'thomaspt2016@example.com',
                [user.email],
                fail_silently=False,
                )
            u = len(str(otp))
            return render(request,'common:verify',{'lenth':u})
        else:
            print("form is not valid")
            return render(request, 'common/sighnup.html', {'form': form_instance})
        
class OtpVerificationView(View):
    def post(self,request):
        print(len(request.POST))
        print(request.POST)
        return HttpResponse("complered")

        # totp = int(request.POST.get['otp1']+request.POST.get['otp2']
        #            +request.POST.get['otp3']+request.POST.get['otp4']
        #            +request.POST.get['otp5']+request.POST.get['otp6'])
        # print(totp)
        # print(type(totp))
        # try:
        #     u=CustomUser.objects.get(otp=totp)
        #     u.is_active=True
        #     u.is_verified=True
        #     u.otp=None
        #     u.save()
        #     return redirect('common:verify')
        # except:
        #     print("Invalid otp")
        #     messages.error(request, 'Invalid OTP. Please try again.')
        #     return redirect('common:verify')

    def get(self,request):
        return render(request,'common/otpverifiy.html')

class LoginformView(View):
    def get(self, request):
        return render(request, 'common/login.html')

class ContactusView(View):
    def get(self, request):
        return render(request, 'common/contactus.html')