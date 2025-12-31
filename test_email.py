import os
import django
from django.conf import settings
from django.core.mail import send_mail

# Configurer l'environnement Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projet.settings')
django.setup()

print("📧 Test d'envoi d'email aux différents rôles...")

contacts = {
    'Operator': settings.OPERATOR_CONTACT,
    'Chief': settings.CHIEF_CONTACT,
    'Manager': settings.MANAGER_CONTACT,
}

for role, contact in contacts.items():
    email = contact['email']
    print(f"\n📨 Envoi à {role} ({email})...")
    
    try:
        send_mail(
            f'Test Email System - {role}',
            f'Ceci est un test pour vérifier la configuration SMTP pour le rôle {role}.',
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
        )
        print(f"✅ Email envoyé avec succès à {role} !")
    except Exception as e:
        print(f"❌ Échec de l'envoi à {role} : {e}")
