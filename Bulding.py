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
from common.models import Building, CustomUser

def populate_buildings_with_custom_logic():
    """
    Populates the Building table with sample data using the user-defined logic.
    """
    floor_list = ['FF', 'SF', 'TF', 'FoF','FiF']
    # These values will be used for 'building_name', which has max_length=2
    building_num_prefixes = ['B22', 'B23', 'B24', 'B25', 'B26']

    print("Populating buildings with custom logic...")

    # --- Fetch Co-Agent Once ---
    # It's more efficient to fetch the agent once outside the loops.
    # Also, added error handling in case no such agent exists.
    try:
        # Get the first co-agent found. If you have multiple, you might want to
        # implement logic to choose randomly or assign based on certain criteria.
        co_agent = CustomUser.objects.filter(role='coagent').first()
        if not co_agent:
            print("Error: No CustomUser with role 'coagent' found. Please create one before running this script.")
            return # Exit the function if no agent to assign
        print(f"Successfully retrieved co-agent: {co_agent.username}")
    except Exception as e:
        print(f"An error occurred while trying to fetch a co-agent: {e}")
        return

    created_count = 0
    # Outer loop to iterate through the building number prefixes
    for building_name_val in building_num_prefixes:
        for floor_abbr in floor_list:
            # Assuming 'rooms' from 1 to 99 for each floor
            for room_number in range(1, 100):

                # 'building_id' is an AutoField, so we don't set it manually.
                # It will be generated automatically by the database.

                try:
                    # Use building_name, floors, and rooms as the lookup parameters
                    # for get_or_create to ensure logical uniqueness.
                    # The 'defaults' dictionary provides values only if a new object is created.
                    building, created = Building.objects.get_or_create(
                        building_name=building_name_val,
                        floors=floor_abbr,
                        rooms=room_number,
                        defaults={
                            'Agent': co_agent # Assign the fetched co-agent
                        }
                    )
                    if created:
                        print(f"Created Building: Name={building.building_name}, Floors={building.floors}, Rooms={building.rooms} (ID: {building.building_id})")
                        created_count += 1
                    else:
                        print(f"Building (Name={building.building_name}, Floors={building.floors}, Rooms={building.rooms}) already exists. Skipping.")

                except Exception as e:
                    print(f"Error processing building data (Name: {building_name_val}, Floors: {floor_abbr}, Rooms: {room_number}): {e}")

    print(f"\nFinished populating buildings. {created_count} new buildings created.")

if __name__ == "__main__":
    populate_buildings_with_custom_logic()

    print("\n--- Verifying data in the Building table ---")
    all_buildings = Building.objects.all().order_by('building_id')
    if all_buildings.exists():
        for b in all_buildings:
            agent_name = b.Agent.get_full_name() if b.Agent else "No Agent"
            print(f"ID: {b.building_id}, Name: {b.building_name}, Floors: {b.floors}, Rooms: {b.rooms}, Agent: {agent_name}")
        print(f"Total buildings in table: {all_buildings.count()}")
    else:
        print("No buildings found in the table.")