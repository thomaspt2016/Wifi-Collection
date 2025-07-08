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
        form_instance = SignupForm()
        return render(request, 'common/sighnup.html',{'form':form_instance})
    
    def post(self, request):
        form_instance = SignupForm(request.POST)
        if form_instance.is_valid():
            print("form is valid")
            user=form_instance.save(commit=False)
            user.is_active = False
            user.username = user.email
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
            lst = []
            for i in range(u):
                lst.append("otp"+str(i+1))
            return render(request,'common/otpverifiy.html',{'lenth':lst})
        else:
            print("form is not valid in signupview")
            return render(request, 'common/sighnup.html', {'form': form_instance})
        
class OtpVerificationView(View):
    def post(self,request):
        otp1 = request.POST.get('otp1', '')
        otp2 = request.POST.get('otp2', '')
        otp3 = request.POST.get('otp3', '')
        otp4 = request.POST.get('otp4', '')
        otp5 = request.POST.get('otp5', '')
        otp6 = request.POST.get('otp6', '')
        
        try:
            totp = int(f"{otp1}{otp2}{otp3}{otp4}{otp5}{otp6}")
        except ValueError:
            messages.error(request, 'Invalid OTP format. Please try again.')
            return redirect('common:verify') # Redirect back to the verification page
        try:
            u=CustomUser.objects.get(otp=totp)
            u.is_active=True
            u.is_verified=True
            u.otp=None
            u.save()
            messages.success(request, 'Account successfully verified! You can now log in.')
            return redirect('common:login') # Redirect to login page after successful verification
        except CustomUser.DoesNotExist: # Use specific exception for clarity
            print("Invalid otp")
            messages.error(request, 'Invalid OTP. Please try again.')
            return redirect('common:verify')

class LoginformView(View):
    def get(self, request):
        return render(request, 'common/login.html')
    
    def post(self, request):
        name = request.POST.get('username')
        pwd = request.POST.get('password')
        print(name, pwd)
        user = authenticate(username=name, password=pwd)
        print(user)
        if user:
            login(request, user)
            u = request.user
            if user.is_superuser:
                return HttpResponse("Login Successfull")
            else:
                return HttpResponse("Login Successfull")
        else:
            print("Invalid user credentials")
            return HttpResponse("Invalid username or password")

class ContactusView(View):
    def get(self, request):
        return render(request, 'common/contactus.html')
