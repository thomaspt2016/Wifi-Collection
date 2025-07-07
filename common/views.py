from django.shortcuts import render
from django.views import View

# Create your views here.

class Homeview(View):
    def get(self,request):
        return render(request, 'common/home.html')

class AboutUsview(View):
    def get(self,request):
        return render(request, 'common/aboutus.html')