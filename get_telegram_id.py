import requests
import json

# Your Token
TOKEN = '8118310302:AAHyeeLk637nPhJty9VUEzhcAaoTLCa79AA'

def get_chat_id():
    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
    print(f"Checking for messages on: {url}")
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if not data['ok']:
            print(f"❌ Error: {data.get('description')}")
            return

        updates = data['result']
        if not updates:
            print("⚠️ No messages found. Please send 'Hello' to your bot on Telegram and run this script again.")
            return

        # Get the chat ID from the last message
        last_update = updates[-1]
        chat_id = last_update['message']['chat']['id']
        username = last_update['message']['chat'].get('username', 'Unknown')
        
        print("\n✅ FOUND CHAT ID!")
        print(f"User: {username}")
        print(f"Chat ID: {chat_id}")
        print("\n👉 Copy this number and paste it into settings.py as TELEGRAM_CHAT_ID")
        
    except Exception as e:
        print(f"❌ Connection Error: {e}")

if __name__ == "__main__":
    get_chat_id()
