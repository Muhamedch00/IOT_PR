import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projet.settings')
django.setup()

from django.contrib.auth.models import User

def create_superuser():
    username = 'admin'
    email = 'admin@example.com'
    password = 'adminpassword123'

    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(username, email, password)
        print(f"✅ Superuser created successfully!")
    else:
        u = User.objects.get(username=username)
        u.set_password(password)
        u.save()
        print(f"🔄 Superuser '{username}' exists. Password reset to '{password}'.")
        
    print(f"👤 Username: {username}")
    print(f"🔑 Password: {password}")

if __name__ == "__main__":
    create_superuser()
