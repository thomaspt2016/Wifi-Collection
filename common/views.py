from django.shortcuts import render
from django.views import View

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
        return render(request, 'common/sighnup.html')

class LoginformView(View):
    def get(self, request):
        return render(request, 'common/login.html')

class ContactusView(View):
    def get(self, request):
        return render(request, 'common/contactus.html')