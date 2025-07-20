from django.db import models
from django.contrib.auth.models import AbstractUser
from random import randint
# Create your models here.


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False) # After verification it will set to True
    otp = models.CharField(max_length=10, null=True, blank=True)
    role = models.CharField(max_length=100, null=True, blank=True, default="client")
    date_joined = models.DateTimeField(auto_now_add=True)

    def generate_otp(self):
        otp_number=str(randint(1000,9999))+str(self.id)
        self.otp=otp_number
        self.save()
        return otp_number


class Building(models.Model):
    building_id = models.AutoField(primary_key=True)
    building_name = models.CharField(max_length=2)
    floors = models.CharField(max_length=10)
    rooms = models.IntegerField()
    Agent = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='buildings_managed',blank=True,null=True)


class InternetPlan(models.Model):
    plan_id = models.AutoField(primary_key=True)
    PLAN_TYPE_CHOICES = [
        ('monthly', 'Monthly'),
        ('temporary', 'Temporary'),
    ]

    plan_name = models.CharField(max_length=100)
    plan_price = models.DecimalField(max_digits=10, decimal_places=0)
    plan_type = models.CharField(
        max_length=10,
        choices=PLAN_TYPE_CHOICES,
        default='monthly', # Set a default value if desired
    )
    Num_Devices = models.IntegerField() # Assuming number of devices is an integer

    def __str__(self):
        return self.plan_name

class WifiCodeUpload(models.Model):
    codeupid = models.AutoField(primary_key=True)
    uploadeddate = models.DateTimeField(auto_now_add=True)
    uploadstatus = models.CharField(max_length=20, default="Initiated")
    uploadedby = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='uploaded_wifi_codes') # Added related_name
    uploadedto = models.FileField(upload_to='wifi_codes')
    remarks = models.CharField(max_length=100, null=True, blank=True)

class CodePoool(models.Model):
    codeid = models.AutoField(primary_key=True)
    code = models.CharField(max_length=20)
    is_used = models.BooleanField(default=False)
    assignedto = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True, related_name='assigned_codes') # Added related_name
    assigneddate = models.DateTimeField(null=True, blank=True)
    exiprydate = models.DateField(null=True, blank=True)
    deactivated = models.DateField(null=True, blank=True)
    sourcepdf = models.ForeignKey(WifiCodeUpload, on_delete=models.CASCADE,blank=True,related_name="Source")




class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE,related_name="profileuser")
    builing_id = models.ForeignKey(Building, on_delete=models.CASCADE,null=True,blank=True, related_name='building')
    bulding = models.CharField()
    floor = models.CharField()
    room = models.CharField()
    phone = models.CharField(max_length=20)
    profpic = models.ImageField(upload_to='profile_pics', null=True, blank=True, default='profile_pics/default_profile.webp')
    is_billable = models.BooleanField(default=True)
    profile_comp = models.BooleanField(default=False)
    plan = models.ForeignKey(InternetPlan, on_delete=models.CASCADE, null=True, blank=True,related_name='plan')
    plan_start_date = models.DateField(null=True, blank=True)
    next_billdate = models.DateField(null=True, blank=True)
    planenddate = models.DateField(null=True, blank=True)


    def __str__(self):
        return f"Profile of {self.user.username}"
    