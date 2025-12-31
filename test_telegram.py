import os
import django
import requests
from django.conf import settings

# Configurer l'environnement Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projet.settings')
django.setup()

def send_telegram_test():
    token = settings.TELEGRAM_BOT_TOKEN
    
    contacts = {
        'Operator': settings.OPERATOR_CONTACT,
        'Chief': settings.CHIEF_CONTACT,
        'Manager': settings.MANAGER_CONTACT,
    }

    print("🚀 Envoi du test Telegram aux différents rôles...")
    print(f"Token: {token[:10]}...")

    for role, contact in contacts.items():
        chat_id = contact.get('telegram_chat_id')
        if not chat_id:
            print(f"⚠️ Pas de Chat ID configuré pour {role}")
            continue
            
        message = f"🔔 Test système IoT - Notification pour le rôle {role}"
        print(f"\n📨 Envoi à {role} (Chat ID: {chat_id})...")

        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            'chat_id': chat_id,
            'text': message
        }

        try:
            response = requests.post(url, data=payload)
            res_json = response.json()
            
            if res_json.get('ok'):
                print(f"✅ Message envoyé avec succès à {role} !")
            else:
                print(f"❌ Erreur pour {role} : {res_json.get('description')}")
                
        except Exception as e:
            print(f"❌ Erreur de connexion pour {role} : {e}")

if __name__ == "__main__":
    send_telegram_test()
