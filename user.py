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
from common.models import Building, CustomUser, Profile
from django.db import IntegrityError # Import for handling potential unique constraint errors
import django.utils.timezone # Import for datetime.now()

def generate_random_email(base_name, domain="example.com"):
    """Generates a random email address based on a given base name for uniqueness."""
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return f"{base_name}_{random_suffix}@{domain}"

def generate_random_phone_number():
    """Generates a random 9-digit phone number as a string."""
    # Ensure the first digit is not 0
    first_digit = str(random.randint(1, 9))
    remaining_digits = ''.join(random.choices(string.digits, k=8))
    return first_digit + remaining_digits

print(f"Script started at: {django.utils.timezone.now()}")

# Fetch all building objects once
buildings = Building.objects.all()

if not buildings.exists():
    print("No Building objects found in the database. Please create some Building instances first.")
    print("Example: Building.objects.create(building_name='A', floors='10', rooms=50, Agent=some_agent_user)")
    exit(1)

print(f"Found {buildings.count()} buildings to process.")

# Loop through each Building object
for building_idx, building_obj in enumerate(buildings):
    print(f"\n--- Processing Building: {building_obj.building_name} (ID: {building_obj.building_id}), Floor: {building_obj.floors}, Room count (from Building model): {building_obj.rooms} ---")

    # Inner loop to create at least 4 people for this 'room' (Building entry)
    NUM_PEOPLE_PER_ROOM = 4
    for person_idx in range(NUM_PEOPLE_PER_ROOM):
        print(f"  Creating person {person_idx + 1} for this building...")

        try:
            # Generate unique parts for each person in this room
            generated_email = generate_random_email(f"client{building_idx+1}_{person_idx+1}", domain="client.com")
            first_name = f"FirstName_{building_obj.building_name}{building_obj.floors}_{person_idx+1}"
            last_name = f"LastName_{building_obj.building_name}{building_obj.floors}_{person_idx+1}"
            
            # Create CustomUser
            us = CustomUser.objects.create_user(
                username=generated_email, # <--- ADDED THIS LINE: Username is same as email
                email=generated_email,
                first_name=first_name,
                last_name=last_name,
                password='Madura%321', # This password will be hashed by create_user
                is_active=True,
                role='client',
            )
            # us.save() # create_user already saves the user
            print(f"    Created CustomUser: {us.username} ({us.email})")

            # Create Profile linked to the CustomUser and the Building object
            prof = Profile.objects.create(
                user=us,
                builing_id=building_obj, # Assign the actual Building object (ForeignKey)
                bulding=building_obj.building_name, # Denormalized char field
                floor=building_obj.floors,           # Denormalized char field
                room=str(building_obj.rooms),        # Denormalized char field, ensure it's string
                phone=generate_random_phone_number(),
                is_billable=True,
                profile_comp=True,
                # plan and plan_start_date are nullable, so they can be left out or set explicitly
            )
            print(f"    Created Profile for {us.username} linked to Building {building_obj.building_name}")

        except IntegrityError as e:
            print(f"    Skipping creation due to IntegrityError (e.g., duplicate email/username): {e}")
        except Exception as e:
            print(f"    An unexpected error occurred during creation: {e}")

print("\nDatabase population script finished.")
print(f"Script ended at: {django.utils.timezone.now()}")