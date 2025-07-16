import os
import django
import random

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

# Now you can import your models
# Replace 'common' with your actual app's name if it's different
from common.models import Building

bul= Building.objects.values_list('building_name', flat=True).distinct()
print(bul)