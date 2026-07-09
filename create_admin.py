# import os
# import django

# # Setup Django environment
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lifelink.settings')
# django.setup()

# from django.contrib.auth.models import User

# # Check if an admin already exists. If not, create one!
# if not User.objects.filter(is_superuser=True).exists():
#     # CHANGE THESE STRINGS TO YOUR DESIRED CREDENTIALS
#     User.objects.create_superuser('syamala', 'syamala@gmail.com', '123456789')
#     print("Superuser automatically created!")
# else:
#     print("Superuser already exists. Skipping.")


import os
import django
import random

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lifelink.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import UserProfile  # Adjust 'core' if your app folder has a different name

print("--- Starting Database Seeding Process ---")

# 1. Create Second Superadmin if it doesn't exist
# 1. Create Second Superadmin if it doesn't exist
secondary_admin_username = 'malleswari' 
if not User.objects.filter(username=secondary_admin_username).exists():
    User.objects.create_superuser(
        username='malleswari', 
        email='malleswari@gmail.com', 
        password='987654321'
    )
    print(f"✔ Superadmin '{secondary_admin_username}' successfully created!")
else:
    print(f"ℹ Superadmin '{secondary_admin_username}' already exists. Skipping.")


# 2. Bulk Create Donors if the database is thin
# We check if we already have mock donors to prevent adding them on every single deployment
if UserProfile.objects.filter(role='Donor').count() < 5:
    
    # Pre-defined pool of diverse data to mix and match
    blood_groups = ['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-']
    organs = ['Kidney', 'Liver', 'Heart', 'Cornea', 'Lungs', 'Pancreas']
    cities = ['Hyderabad', 'Visakhapatnam', 'Vijayawada', 'Tirupati', 'Guntur', 'Nellore', 'Rajahmundry']
    
    mock_names = [
        ('mukesh_k', 'Mukesh Kumar'), ('srinivas_m', 'Srinivas Rao'), 
        ('priya_sharma', 'Priya Sharma'), ('divya_t', 'Divya Teja'),
        ('kiran_b', 'Kiran Babu'), ('sandeep_v', 'Sandeep Varma'),
        ('harika_p', 'Harika P.'), ('syam', 'Syam'),
        ('anjali_s', 'Anjali Singh'), ('venkat_r', 'Venkat Ramana'),
        ('ramesh_g', 'Ramesh G.'), ('kavitha_m', 'Kavitha Murthy')
    ]

    for index, (username, full_name) in enumerate(mock_names, start=1):
        if not User.objects.filter(username=username).exists():
            # Create base user authentication account
            user = User.objects.create_user(
                username=username,
                email=f"{username}@example.com",
                password='DonorPassword123!'
            )
            
            # Split full name for first/last name fields if needed
            name_parts = full_name.split(' ')
            user.first_name = name_parts[0]
            if len(name_parts) > 1:
                user.last_name = name_parts[1]
            user.save()

            # Create corresponding UserProfile matching your model fields
            UserProfile.objects.create(
                user=user,
                role='Donor',
                blood_group=random.choice(blood_groups),
                organ_pledge=random.choice(organs),
                city=random.choice(cities),
                phone=f"+91 98480{random.randint(10000, 99999)}"
            )
            print(f"✔ Created Donor {index}/12: {username} ({full_name})")
            
    print("--- Seeding Completed Successfully! ---")
else:
    print("ℹ Existing donor profiles detected. Seeding skipped to avoid duplication.")