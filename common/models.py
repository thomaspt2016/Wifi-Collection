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
    Agent = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='buildings_managed')

class InternetPlan(models.Model):
    plan_id = models.AutoField(primary_key=True)
    plan_name = models.CharField(max_length=20)
    plan_price = models.IntegerField()
    plan_type = models.CharField(max_length=20)
    plan_period = models.CharField(max_length=20)
    is_Active = models.BooleanField(default=True)
    Num_Devices = models.IntegerField()

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
    device = models.CharField(max_length=20)
    is_used = models.BooleanField(default=False)
    assignedto = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True, related_name='assigned_codes') # Added related_name
    assigneddate = models.DateTimeField(null=True, blank=True)
    deactivated = models.DateField(null=True, blank=True)
    sourcepdf = models.ForeignKey(WifiCodeUpload, on_delete=models.CASCADE)


class Billgeneration(models.Model):
    billdate = models.DateTimeField(auto_now_add=True)
    billamount = models.IntegerField()
    billstatus = models.CharField(max_length=20)
    billgeneratedby = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='bills_generated')
    billgeneratedfor = models.OneToOneField(CustomUser, on_delete=models.PROTECT, related_name='bills_received', null=True, blank=True)
    billgeneratedforplan = models.OneToOneField(InternetPlan, on_delete=models.PROTECT, null=True, blank=True)
    billgendate = models.DateTimeField(auto_now_add=True)
    paymentid = models.CharField(max_length=20, null=True, blank=True)
    InvoiceNo = models.CharField(max_length=20, null=False, blank=False, primary_key=True)

class Payment(models.Model):
    paymentfor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='payments_received')
    paymentforplan = models.ForeignKey(InternetPlan, on_delete=models.CASCADE)
    paymentforbill = models.ForeignKey(Billgeneration, on_delete=models.CASCADE)
    paymentid = models.CharField(max_length=20, null=True, blank=True)
    paymentdate = models.DateTimeField(auto_now_add=True)
    paymentamount = models.IntegerField()
    paymentstatus = models.CharField(max_length=20)
    paymentmode = models.CharField(max_length=20)
    collectedby = models.CharField()

class Ticket(models.Model):
    agent = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='tickets_assigned')
    raised = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='tickets_raised')
    ticketid = models.AutoField(primary_key=True)
    ticketdate = models.DateTimeField(auto_now_add=True)
    ticketstatus = models.CharField(max_length=20)
    ticketsub = models.CharField(max_length=100)
    priority = models.CharField(max_length=20, default="Low")
    ticketdesc = models.CharField(max_length=100)
    ticketupdate = models.DateField(auto_now_add=True)
    attachment = models.FileField(upload_to='ticket_attachments', null=True, blank=True)


class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    buildingid = models.ForeignKey(Building, on_delete=models.CASCADE, null=True, blank=True)
    phone = models.CharField(max_length=20)
    profpic = models.ImageField(upload_to='profile_pics', null=True, blank=True, default='profile_pics/default_profile.webp')
    is_billable = models.BooleanField(default=True)
    profile_comp = models.BooleanField(default=False)

    def __str__(self):
        return f"Profile of {self.user.username}"