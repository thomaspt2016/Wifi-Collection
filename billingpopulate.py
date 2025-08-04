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

from common.models import Building, CustomUser, Profile, InternetPlan, CodePoool, Payment,BillingPlan
from django.utils import timezone

internetplans = InternetPlan.objects.all()
usrd = CustomUser.objects.filter(role="client")
CodePo = CodePoool.objects.filter(is_used=False)

# Check if there are plans and users to populate with
if not internetplans:
    print("No InternetPlan objects found. Please create some plans first.")
    exit(1)
if not usrd:
    print("No CustomUser objects with role 'client' found.")
    exit(1)
if not CodePo:
    print("No CodePoool objects with is_used=False found.")
    exit(1)
def paymencode(id):
    pay0bj = Payment.objects.filter(payment_user=id)
    if pay0bj.exists():
        return pay0bj

for user in usrd:
    BillingPlan.objects.create(
        billing_user=user,
        billing_plan=random.choice(internetplans),
        billingplan = random.choice(paymencode(user)),
        billing_code = random.choice(CodePo),
        billing_status = random.choice(["Success", "Failed"]),
        billing_date = random.choice([timezone.now(), timezone.now() - datetime.timedelta(days=1)]),
    )
