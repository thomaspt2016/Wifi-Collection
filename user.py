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
# --- End Django Setup ---

# Import your models AFTER django.setup()
from common.models import Building, CustomUser, Profile, InternetPlan, CodePoool

# Fetch all available (unused) codes into a list of CodePoool objects
available_codes_pool = list(CodePoool.objects.filter(is_used=False))

if not available_codes_pool:
    print("No available (unused) codes found in CodePoool. Please add some codes first.")
    exit(1)

# Fetch users, excluding owners, and prefetch their profile and internet plan.
users_to_assign_queryset = CustomUser.objects.exclude(role="owner").prefetch_related('profileuser__plan')
users_to_assign_list = list(users_to_assign_queryset) # Convert queryset to list for random.choice

if not users_to_assign_list:
    print("No non-owner users found to assign codes to.")
    exit(1)

print(f"Found {len(available_codes_pool)} available codes.")
print(f"Found {len(users_to_assign_list)} non-owner users.")

# --- Code Assignment Logic ---
assigned_count = 0
max_assignments = 60 # The target total number of codes to assign

# Keep track of users we've tried and couldn't fully assign in this iteration
# This prevents an infinite loop if only unassignable users remain
skipped_users_in_cycle = set()
original_users_count = len(users_to_assign_list)

while assigned_count < max_assignments:
    # Break conditions if we run out of resources
    if not available_codes_pool:
        print(f"\nRan out of available codes in the pool. Assigned {assigned_count}/{max_assignments} codes.")
        break
    if not users_to_assign_list: # If all users were processed/skipped
        print(f"\nRan out of available users to assign codes to. Assigned {assigned_count}/{max_assignments} codes.")
        break

    # If we've cycled through all users and couldn't assign to any, break to prevent infinite loop
    if len(skipped_users_in_cycle) == original_users_count:
        print(f"\nNo users could be fully assigned without exceeding the limit or due to insufficient codes. Assigned {assigned_count}/{max_assignments} codes.")
        break

    # Select a user, but ensure we don't pick a user we just skipped in this cycle
    user = None
    eligible_users = [u for u in users_to_assign_list if u.pk not in skipped_users_in_cycle]
    if not eligible_users:
        # All remaining users have been skipped in this cycle, reset and try again
        # This handles cases where conditions might change (e.g., more codes become available)
        # but for this script, conditions are static so this implies no more assignable users.
        print(f"\nNo more eligible users to pick in this cycle. Assigned {assigned_count}/{max_assignments} codes.")
        break
    user = random.choice(eligible_users)
    
    print(f"\nAttempting to process user: {user.username} (Current total assigned: {assigned_count}/{max_assignments})")

    # --- Pre-assignment checks for full assignment ---
    num_devices_to_assign = 0
    if hasattr(user, 'profileuser') and user.profileuser:
        if user.profileuser.plan:
            num_devices_to_assign = user.profileuser.plan.Num_Devices
        else:
            print(f"  User {user.username} has a profile but no InternetPlan assigned. Skipping.")
            skipped_users_in_cycle.add(user.pk) # Mark as skipped for this cycle
            continue
    else:
        print(f"  User {user.username} does not have a profile. Skipping.")
        skipped_users_in_cycle.add(user.pk) # Mark as skipped for this cycle
        continue

    if num_devices_to_assign <= 0:
        print(f"  User {user.username} has a plan with 0 or negative devices. Skipping.")
        skipped_users_in_cycle.add(user.pk) # Mark as skipped for this cycle
        continue
    
    # Crucial check: Can we assign ALL required codes to this user without exceeding max_assignments?
    if assigned_count + num_devices_to_assign > max_assignments:
        print(f"  Assigning {num_devices_to_assign} codes to {user.username} would exceed the {max_assignments} total limit.")
        print(f"  Current: {assigned_count}, Required: {num_devices_to_assign}, Max: {max_assignments}. Skipping {user.username} for partial assignment prevention.")
        skipped_users_in_cycle.add(user.pk) # Mark as skipped for this cycle
        continue # Skip this user and try another

    # Crucial check: Are there enough available codes for this user's full assignment?
    if len(available_codes_pool) < num_devices_to_assign:
        print(f"  Not enough available codes ({len(available_codes_pool)}) to fully assign {num_devices_to_assign} codes to {user.username}.")
        skipped_users_in_cycle.add(user.pk) # Mark as skipped for this cycle
        continue # Skip this user and try another

    print(f"  User's plan requires {num_devices_to_assign} devices. Proceeding with full assignment.")
    # Reset skipped users, as we successfully picked one
    skipped_users_in_cycle.clear() 

    # Assign codes for this user
    assigned_codes_for_user = [] # Temporarily store codes assigned to this user
    try:
        for j in range(num_devices_to_assign):
            code_to_assign = random.choice(available_codes_pool) # Pick an available code

            # Update the CodePoool object in memory first
            code_to_assign.assignedto = user
            code_to_assign.assigneddate = datetime.datetime.today()
            code_to_assign.exiprydate = datetime.date.today() + datetime.timedelta(days=180)
            code_to_assign.is_used = True
            
            assigned_codes_for_user.append(code_to_assign)
            available_codes_pool.remove(code_to_assign) # Remove from in-memory pool immediately

        # If all codes for the user are successfully picked from the pool, then save them
        for code_obj in assigned_codes_for_user:
            code_obj.save() # Persist changes to the database
            assigned_count += 1 # Increment the total assigned count

            print(f"  Assigned code '{code_obj.code}' to {user.username} (Code {assigned_codes_for_user.index(code_obj)+1}/{num_devices_to_assign} for user; Total assigned: {assigned_count}/{max_assignments}).")

    except Exception as e:
        print(f"  Error during assignment for {user.username}: {e}. Rolling back codes picked for this user.")
        # If any error occurs during the inner loop, roll back the codes to available_codes_pool
        # This is a simple in-memory rollback. For true database transactions, use Django's transaction API.
        for code_obj in assigned_codes_for_user:
            available_codes_pool.append(code_obj) # Add them back to the in-memory pool
        skipped_users_in_cycle.add(user.pk) # Mark user as skipped for this cycle
        continue # Skip to the next user in the outer loop

print(f"\nScript finished. Total codes assigned: {assigned_count} (Target: {max_assignments})")