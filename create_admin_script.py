# Django Shell Script to Create Admin Users
# Run this with: python manage.py shell < create_admin_script.py

from django.contrib.auth.models import User
from blog.models import UserProfile

def create_admin_user(username, email, password, first_name="", last_name=""):
    """
    Helper function to create admin users programmatically.
    """
    if User.objects.filter(username=username).exists():
        print(f"User '{username}' already exists!")
        return None
    
    try:
        # Create the user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            is_staff=True,  # Django admin access
            is_superuser=True  # Full admin permissions
        )
        
        # Create UserProfile with admin role
        user_profile, created = UserProfile.objects.get_or_create(
            user=user,
            defaults={
                'role': 'admin',
                'bio': f'Admin account for {first_name} {last_name}'.strip(),
            }
        )
        
        print(f"Successfully created admin user: {username}")
        print(f"Email: {email}")
        print(f"Django Superuser: {user.is_superuser}")
        print(f"Blog Admin Role: {user_profile.role}")
        return user
        
    except Exception as e:
        print(f"Error creating admin user: {str(e)}")
        return None

# Example usage (commented out):
# create_admin_user(
#     username="admin2", 
#     email="admin2@example.com", 
#     password="SecurePass123!", 
#     first_name="Admin", 
#     last_name="Two"
# )

print("Admin user creation script loaded.")
print("Use create_admin_user() function to create additional admin accounts.")