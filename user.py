import os
import django
import random
import string

# --- Django Setup ---
# This part is crucial for running the script outside of manage.py shell
# Replace 'wificollection' with the actual name of your Django project
# (the directory containing settings.py)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wificollection.settings')

# Ensure django.setup() is called immediately after setting the environment variable
try:
    django.setup()
    print("Django environment successfully set up.") # Confirmation print
except Exception as e:
    print(f"Error setting up Django environment: {e}")
    # Exit if setup fails, as models won't be accessible
    exit(1)
# --- End Django Setup ---

# Import your models AFTER django.setup()
from common.models import Building, CustomUser, Profile,InternetPlan
import datetime

users = CustomUser.objects.filter(role='client')
for user in users:
    profile = Profile.objects.get(user=user)
    randomnum = random.randint(1, 3)
    profile.plan = InternetPlan.objects.get(plan_id=randomnum)
    today = datetime.date.today()
    if randomnum ==3:
        profile.plan_start_date = today
        profile.planenddate = today+datetime.timedelta(days=20)
        profile.is_billable = False
    else:
        profile.plan_start_date = today
        next_month_year = today.year
        next_month_month = today.month + 1
        if next_month_month > 12:
            next_month_month = 1
            next_month_year += 1 
        profile.next_billdate = datetime.date(next_month_year, next_month_month, 25)
        profile.is_billable = True
    profile.save()
