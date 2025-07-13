from django.db import models
from django.contrib.auth.models import AbstractUser
from random import randint
# Create your models here.


class CustomUser(AbstractUser):
    email=models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100) 
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_verified=models.BooleanField(default=False)#After verification it will set to True
    otp=models.CharField(max_length=10,null=True,blank=True)
    role = models.CharField(max_length=100, null=True, blank=True,default="client")
    date_joined = models.DateTimeField(auto_now_add=True)

    def generate_otp(self):
        #for creating random otp number for verification
        otp_number=str(randint(1000,9999))+str(self.id)
        self.otp=otp_number
        self.save()
        return otp_number


class Building(models.Model):
    building_id = models.AutoField(primary_key=True)
    building_name = models.CharField(max_length=2)
    floors = models.CharField(max_length=10)
    rooms = models.IntegerField(max_length=3)
    Agent = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

class InternetPlan(models.Model):
    plan_id = models.AutoField(primary_key=True)
    plan_name = models.CharField(max_length=20)
    plan_price = models.IntegerField(max_length=3)
    plan_type = models.CharField(max_length=20)
    plan_period = models.CharField(max_length=20)
    is_Active = models.BooleanField(default=True)
    Num_Devices = models.IntegerField(max_length=2)

class WifiCodeUpload(models.Model):
    codeupid = models.AutoField(primary_key=True)
    uploadeddate = models.DateTimeField(auto_now_add=True)
    uploadstatus = models.CharField(max_length=20,default="Initiated")
    uploadedby = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    uploadedto = models.FileField(upload_to='wifi_codes')
    remarks = models.CharField(max_length=100, null=True, blank=True)

class CodePoool(models.Model):
    codeid = models.AutoField(primary_key=True)
    code = models.CharField(max_length=20)
    device = models.CharField(max_length=20)
    is_used = models.BooleanField(default=False)
    assignedto = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    assigneddate = models.DateTimeField(null=True, blank=True)
    deactivated = models.DateField(null=True, blank=True)
    sourcepdf = models.ForeignKey(WifiCodeUpload, on_delete=models.CASCADE)



class Billgeneration(models.Model):
    billdate = models.DateTimeField(auto_now_add=True)
    billamount = models.IntegerField(max_length=5)
    billstatus = models.CharField(max_length=20)
    billgeneratedby = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    billgeneratedfor = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    billgeneratedforplan = models.ForeignKey(InternetPlan, on_delete=models.CASCADE)
    billgendate = models.DateTimeField(auto_now_add=True)
    billin_start = models.DateTimeField(null=False,blank=False)
    billin_end = models.DateTimeField(null=False, blank=False)
    duedate = models.DateTimeField(null=True, blank=True)
    payeddate = models.DateTimeField(null=True, blank=True)
    paymentid = models.CharField(max_length=20, null=True, blank=True)
    InvoiceNo = models.CharField(max_length=20, null=False, blank=False,primary_key=True)

class Payment(models.Model):
    paymentid = models.AutoField(primary_key=True)
    paymentdate = models.DateTimeField(auto_now_add=True)
    paymentamount = models.IntegerField(max_length=5)
    paymentstatus = models.CharField(max_length=20)
    paymentmode = models.CharField(max_length=20)
    paymentfor = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    paymentforplan = models.ForeignKey(InternetPlan, on_delete=models.CASCADE)
    paymentforbill = models.ForeignKey(Billgeneration, on_delete=models.CASCADE)
    collectedby = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='collected_by')

class Ticket(models.Model):
    ticketid = models.AutoField(primary_key=True)
    ticketdate = models.DateTimeField(auto_now_add=True)
    ticketstatus = models.CharField(max_length=20)
    raised = models.ForeignKey(CustomUser, on_delete=models.CASCADE,default="Visitor")
    agent = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='agent')
    ticketsub = models.CharField(max_length=100)
    priority = models.CharField(max_length=20,default="Low")
    ticketdesc = models.CharField(max_length=100)
    ticketupdate = models.DateField(auto_now_add=True)
    attachment = models.FileField(upload_to='ticket_attachments', null=True, blank=True)


class Profile(models.Model):
    user=models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    Buildingid = models.ForeignKey(Building,on_delete=models.CASCADE)
    BillingType = models.ForeignKey(InternetPlan, on_delete=models.CASCADE)
    phone=models.CharField(max_length=20)
    bulding = models.ForeignKey(Building, on_delete=models.CASCADE)
    Bulding_No = models.IntegerField(max_length=2)
    floor = models.CharField(max_length=2)
    room_no = models.IntegerField(max_length=3)
    profpic = models.ImageField(upload_to='profile_pics', null=True, blank=True,default='profile_pics.webp')
    is_billable = models.BooleanField(default=True)

