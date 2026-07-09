import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lifelink.settings')
django.setup()

from django.contrib.auth.models import User

# Check if an admin already exists. If not, create one!
if not User.objects.filter(is_superuser=True).exists():
    # CHANGE THESE STRINGS TO YOUR DESIRED CREDENTIALS
    User.objects.create_superuser('syamala', 'syamala@gmail.com', '123456789')
    print("Superuser automatically created!")
else:
    print("Superuser already exists. Skipping.")