from django.views import View
from .forms import SignupForm,ProfileForm,UserForm
from django.shortcuts import render,redirect
from django.views import View
from django.http import HttpResponse
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.auth import authenticate,login,logout
from .models import CustomUser,Profile,Building,InternetPlan
from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.

class Homeview(View):
    def get(self,request):
        if request.user.is_authenticated:
            prof = Profile.objects.get(user=request.user)
            if request.user.role == "owner":
                if prof.profile_comp ==False:
                    return redirect('common:profile')
                return redirect('owner:ownclients')
            elif request.user.role == "client":
                if prof.profile_comp ==False:
                    return redirect('common:profile')
                return redirect('clients:cliwificode')
            elif request.user.role == "coagent":
                if prof.profile_comp ==False:
                    return redirect('common:profile')
                return redirect('coagents:coclients') # <-- Redirect for collection agents
            else:
                return render(request, 'common/home.html')
        else:
            return render(request, 'common/home.html')

class AboutUsview(View):
    def get(self,request):
        return render(request, 'common/aboutus.html')

class PricingView(View):
    def get(self, request):
        plans = InternetPlan.objects.filter(planstatus=True)
        context = {'plans':plans}
        return render(request, 'common/pricing.html',context)

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
            messages.success(request, 'Signup successful! An OTP has been sent to your email for verification.')
            u = len(str(otp))
            lst = []
            for i in range(u):
                lst.append("otp"+str(i+1))
            return render(request,'common/otpverifiy.html',{'lenth':lst,'useris':user.id})
        else:
            print("form is not valid in signupview")
            messages.error(request, 'Invalid form data. Please correct the errors.')
            return render(request, 'common/sighnup.html', {'form': form_instance})
class OTPResendView(View):
    def get(self, request,id):
        try:
            user = CustomUser.objects.get(id=id)
            otp = user.generate_otp()
            send_mail(
                'OTP Test',
                otp,
                'thomaspt2016@example.com',
                [user.email],
                fail_silently=False,
                )
            messages.success(request, 'OTP resent successfully!')
            u = len(str(otp))
            lst = []
            for i in range(u):
                lst.append("otp"+str(i+1))
            return render(request, 'common/otpverifiy.html', {'lenth':lst, 'useris':user.id})
        except CustomUser.DoesNotExist:
            messages.error(request, 'User not found.')
            return redirect('common:signup')
        
class OtpVerificationView(View):
    def get(self, request):
        return render(request, 'common/otpverifiy.html')

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
            try:
                Profile.objects.create(user=u)
            except Exception as e:
                messages.error(request, 'Profile already exists.')
                print(e)
                return redirect('common:verify')
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
            prof = Profile.objects.get(user=user)
            login(request, user)
            if user.role == "owner":
                if prof.profile_comp ==False:
                    return redirect('common:profile')
                messages.success(request, 'Login successful!')
                return redirect('owner:ownerhome')
    
            elif user.role == "client":
                if prof.profile_comp ==False:
                    return redirect('common:profile')
                else:
                    messages.success(request, 'Login successful!')
                    return redirect ('clients:clienthome')
            
            elif user.role == "coagent":
                if prof.profile_comp ==False:
                    return redirect('common:profile')
                else:
                    messages.success(request, 'Login successful!')
                    return redirect ('coagents:cohome')
            else:
                return HttpResponse("No valid Cred")
            
        else:
            print("Invalid user credentials")
            messages.error(request, 'Invalid username or password. Please try again.')
            return HttpResponse("Invalid username or password")

class ContactusView(View):
    def get(self, request):
        return render(request, 'common/contactus.html')

class SignoutView(View):
    def get(self,request):
        logout(request)
        return redirect('common:home')

class ProfileView(View,LoginRequiredMixin):
    def get(self,request):
        form_instance = ProfileForm()
        prof_pic = Profile.objects.get(user=request.user) 
        return render(request, 'common/profile.html', {'form': form_instance,"page_title":"Profile",'pic':prof_pic})
    
    def post(self,request):
        print(request.POST)
        profin = Profile.objects.get(user=request.user)
        if request.FILES:
            forminst = ProfileForm(request.POST, request.FILES,instance=profin)
            if forminst.is_valid():
                print("form is valid")
                prof = forminst.save(commit=False)
                prof.profile_comp = True
                prof.builing_id = Building.objects.get(building_name=request.POST.get('bulding'),
                                                       floors=request.POST.get('floor'),
                                                       rooms=request.POST.get('room'))
                prof.save()
                return redirect('common:home')
        else:
            forminst = ProfileForm(request.POST,instance=profin)
            if forminst.is_valid():
                print("form is valid")
                prof = forminst.save(commit=False)
                prof.profile_comp = True
                prof.builing_id = Building.objects.get(building_name=request.POST.get('bulding'),
                                                       floors=request.POST.get('floor'),
                                                       rooms=request.POST.get('room'))
                prof.profpic = f'profile_pics/default_profile.webp'
                prof.save()
                return redirect('common:home')

class ProfileEditView(View, LoginRequiredMixin):
    def get(self, request, id):
        try:
            userd = CustomUser.objects.get(id=id)
            prof = Profile.objects.get(user=userd)
        except (CustomUser.DoesNotExist, Profile.DoesNotExist):
            return redirect('common:home')

        form_instance = ProfileForm(instance=prof)
        forminst2 = UserForm(instance=userd)

        context = {
            'form': form_instance,
            'form2': forminst2,
            'pic': prof,
            'page_title': 'Edit Profile',
        }

        if request.user.role == "owner":
            return render(request, 'owner/editprofile.html', context)
        elif request.user.role == "client":
            print("inside role")
            return render(request, 'client/editprofile.html', context)
        elif request.user.role == "coagent":
            return render(request, 'coagent/editprofile.html', context)
        else:
            # Handle cases where role is not recognized
            return redirect('common:home')

    def post(self, request, id):
        try:
            userd = CustomUser.objects.get(id=id)
            prof = Profile.objects.get(user=userd)
        except (CustomUser.DoesNotExist, Profile.DoesNotExist):
            return redirect('common:home')

        if 'submit_user_form' in request.POST:
            forminst2 = UserForm(request.POST, instance=userd)
            if forminst2.is_valid():
                forminst2.save()
        elif 'submit_profile_form' in request.POST:
            form_instance = ProfileForm(request.POST, request.FILES, instance=prof)
            if form_instance.is_valid():
                form_instance.save()

        form_instance = ProfileForm(instance=prof)
        forminst2 = UserForm(instance=userd)

        context = {
            'form': form_instance,
            'form2': forminst2,
            'pic': prof,
            'page_title': 'Edit Profile',
        }

        # Render the appropriate template based on role after POST
        if request.user.role == "owner":
            return render(request, 'owner/editprofile.html', context)
        elif request.user.role == "client":
            return render(request, 'client/editprofile.html', context)
        elif request.user.role == "coagent":
            return render(request, 'coagent/editprofile.html', context)
        else:
            return redirect('common:home')

class ContacformEmail(View):
    def post(self, request):
        print(request.POST)
        owne = CustomUser.objects.filter(role="owner").first()
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message'," ")
        print(email, subject, message)
        send_mail(
            subject,
            message,
            email,
            [owne.email],
            fail_silently=False,
            )
        messages.success(request, 'Email sent successfully!')
        return redirect('common:contactus')
class PrivacyPolicy(View):
    def get(self, request):
        return render(request, 'common/privacy.html')
    
class TermsandConditions(View):
    def get(self, request):
        return render(request, 'common/terms.html')