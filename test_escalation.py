import requests
import time

# URL de l'API (adapté à votre port local)
url = 'http://127.0.0.1:8000/api/post'

# Simulation d'une température très élevée (Incident)
data = {
    'temp': 50.0,
    'hum': 30.0
}

print("🔥 Démarrage de la simulation d'incidents...")

# 1. Première Alerte -> Création Ticket (Opérateur)
print("\n--- Envoi Alerte 1 (Création) ---")
try:
    response = requests.post(url, data=data)
    print(f"Status: {response.status_code}")
except Exception as e:
    print(f"Erreur: {e}")
time.sleep(2)

# 2. Deuxième Alerte -> Escalade vers CHEF (selon la règle '2 fois')
print("\n--- Envoi Alerte 2 (Escalade Chef) ---")
try:
    response = requests.post(url, data=data)
    print(f"Status: {response.status_code}")
except Exception as e:
    print(f"Erreur: {e}")
time.sleep(2)

# 3. Troisième Alerte -> Reste Chef (1ère alerte chef)
print("\n--- Envoi Alerte 3 (Persistance Chef 1) ---")
try:
    response = requests.post(url, data=data)
    print(f"Status: {response.status_code}")
except Exception as e:
    print(f"Erreur: {e}")
time.sleep(2)

# 4. Quatrième Alerte -> Escalade Manager (2ème alerte chef -> Manager)
print("\n--- Envoi Alerte 4 (Escalade Manager) ---")
try:
    response = requests.post(url, data=data)
    print(f"Status: {response.status_code}")
except Exception as e:
    print(f"Erreur: {e}")

print("\n✅ Simulation terminée. Vérifiez vos emails et le terminal Django pour les logs.")
