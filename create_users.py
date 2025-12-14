import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projet.settings')
django.setup()

from django.contrib.auth.models import User, Group

def create_users():
    roles = ['Operator', 'Chief', 'Manager']
    
    for role in roles:
        username = role.lower()
        email = f"{username}@example.com"
        password = "password123"
        
        if not User.objects.filter(username=username).exists():
            user = User.objects.create_user(username, email, password)
            print(f"✅ Created user: {username} / {password}")
            
            # Create group if not exists
            group, created = Group.objects.get_or_create(name=role)
            user.groups.add(group)
        else:
            print(f"ℹ️ User {username} already exists.")

if __name__ == "__main__":
    create_users()
