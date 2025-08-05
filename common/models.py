from django.db import models
from django.contrib.auth.models import AbstractUser
from random import randint
import datetime as dt
import uuid
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
        otp_number=str(randint(1000,9999))
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
    planstatus = models.BooleanField(default=False) 

    def __str__(self):
        return self.plan_name

class WifiCodeUpload(models.Model):
    codeupid = models.AutoField(primary_key=True)
    uploadeddate = models.DateTimeField(auto_now_add=True)
    uploadstatus = models.CharField(max_length=20, default="Initiated")
    uploadedby = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='uploaded_wifi_codes')
    uploadedto = models.FileField(upload_to='wifi_codes')
    remarks = models.CharField(max_length=100, null=True, blank=True)

class CodePoool(models.Model):
    codeid = models.AutoField(primary_key=True)
    code = models.CharField(max_length=20)
    is_used = models.BooleanField(default=False)
    assignedto = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True, related_name='assigned_codes')
    assigneddate = models.DateTimeField(null=True, blank=True)
    exiprydate = models.DateField(null=True, blank=True)
    deactivated = models.DateField(null=True, blank=True)
    is_deactivated = models.BooleanField(default=False)
    sourcepdf = models.ForeignKey(WifiCodeUpload, on_delete=models.CASCADE,blank=True,related_name="Source")
    Invoice = models.ForeignKey('Payment', on_delete=models.CASCADE, null=True, blank=True, related_name='Invoice')
    remarks = models.CharField(max_length=100, null=True, blank=True)


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

def generate_payment_id():
    date_str = dt.date.today().strftime("%Y%m%d")
    unique_str = uuid.uuid4().hex[:10]
    return f"{date_str}-{unique_str}"


class Payment(models.Model):
    InvoiceId = models.CharField(primary_key=True, max_length=50, unique=True, default=generate_payment_id)
    payment_date = models.DateField(auto_now_add=True)
    payment_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50)
    payment_status = models.CharField(max_length=20)
    payment_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='paymentsusr')
    payment_plan = models.ForeignKey(InternetPlan, on_delete=models.CASCADE, related_name='paymentsplan')
    online_payment_id = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.InvoiceId
    def save(self, *args, **kwargs):
        if not self.InvoiceId:
            self.InvoiceId = generate_payment_id()
        super().save(*args, **kwargs)

class BillingPlan(models.Model):
    billingid = models.AutoField(primary_key=True)
    paymentid = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='paymentid')
    billingusr = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='billingusr')
    billingplan = models.ForeignKey(InternetPlan, on_delete=models.CASCADE, related_name='billingplan')
    billstartdate = models.DateField(null=True, blank=True)
    billendate = models.DateField(null=True, blank=True)
    PlanStatus = models.CharField(max_length=20, default="Upcoming")


class Ticketing(models.Model):
    ticketid = models.AutoField(primary_key=True)
    ticketdate = models.DateTimeField(auto_now_add=True)
    ticketstatus = models.CharField(max_length=20, default="Open")
    ticketraised = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='tickets_created_by_user')
    ticketto = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='tickets_assigned_to_agent')
    ticketdesc = models.TextField(null=True, blank=True)
    ticketsubj = models.CharField(max_length=255, null=True, blank=True)
    PRIORITY_CHOICES = [
    ('low', 'Low'),
    ('medium', 'Medium'),
    ('high', 'High'),
    ('urgent', 'Urgent'),
]
    ticketpriority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='medium',
        null=True,
        blank=True
    )
    ticketfile = models.FileField(upload_to='tickets', null=True, blank=True)

    def __str__(self):
        return f"Ticket #{self.ticketid} - {self.ticketsubj} by {self.ticketraised.username}"
    class Meta:
        ordering = ['-ticketdate']

class TicketUpdates(models.Model):
    updateid = models.AutoField(primary_key=True)
    ticketid = models.ForeignKey(Ticketing, on_delete=models.CASCADE, related_name='updates')
    ticketupdate = models.DateTimeField(auto_now_add=True)
    ticketupdateby = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='updates_made_by_user')
    ticketupdatefile = models.FileField(upload_to='tickets', null=True, blank=True)
    ticketupdatedesc = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Update for Ticket #{self.ticketid.ticketid} by {self.ticketupdateby.username}"
    class Meta:
        # Added ordering for consistent display of updates within a ticket
        ordering = ['ticketupdate']
        verbose_name_plural = "Ticket Updates"