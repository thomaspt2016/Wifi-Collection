import os
import django
import random
import string
import datetime

# --- Django Setup ---
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wificollection.settings')

try:
    django.setup()
    print("Django environment successfully set up.")
except Exception as e:
    print(f"Error setting up Django environment: {e}")
    exit(1)

from common.models import Building, CustomUser, Profile, InternetPlan, CodePoool, Payment
from django.utils import timezone

internetplans = InternetPlan.objects.all()
usrd = CustomUser.objects.filter(role="client")

# Check if there are plans and users to populate with
if not internetplans:
    print("No InternetPlan objects found. Please create some plans first.")
    exit(1)
if not usrd:
    print("No CustomUser objects with role 'client' found.")
    exit(1)

for user in usrd:
    for i in range(3):
        # Select a random plan to associate with the payment
        random_plan = random.choice([plan for plan in internetplans])
        
        pay = Payment.objects.create(
            payment_user=user,
            # CORRECTED: Access the 'price' attribute from the randomly selected plan
            payment_amount=random_plan.plan_price,
            payment_status=random.choice(["Success", "Failed"]),
            payment_method=random.choice(["Cash", "Online"]),
            payment_plan=random_plan,
            # REMOVED: The 'payment_description' field is not in your Payment model
        )
        if pay.payment_method=="Online":
            pay.online_payment_id = "pay_"+str(random.randint(100000,999999))
            pay.save()
    print(f"Created 3 payments for user {user.username}")
