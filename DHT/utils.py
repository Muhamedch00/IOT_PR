import requests
from django.conf import settings
from django.core.mail import send_mail
import logging

logger = logging.getLogger(__name__)

def send_telegram_message(message):
    """Sends a message to the configured Telegram chat."""
    token = settings.TELEGRAM_BOT_TOKEN
    chat_id = settings.TELEGRAM_CHAT_ID
    
    if not token or not chat_id:
        logger.warning("Telegram token or chat_id not configured.")
        return False
        
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message
    }
    
    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"❌ Failed to send Telegram message: {e}") # DEBUG PRINT
        logger.error(f"Failed to send Telegram message: {e}")
        return False

    print(f"✅ Telegram message sent successfully to {chat_id}!") # DEBUG PRINT
    return True

def send_whatsapp_message(message, to_phone):
    """Sends a WhatsApp message using Cloud API."""
    token = settings.WHATSAPP_TOKEN
    phone_id = settings.WHATSAPP_PHONE_ID
    
    if not token or not phone_id:
        logger.warning("WhatsApp token or phone_id not configured.")
        return False
        
    url = f"https://graph.facebook.com/v17.0/{phone_id}/messages"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to_phone,
        "type": "text",
        "text": {"body": message}
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return True
    except Exception as e:
        logger.error(f"Failed to send WhatsApp message: {e}")
        return False

def send_alert_email(subject, message, recipient_list):
    """Sends an email alert."""
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=recipient_list,
            fail_silently=False
        )
        return True
    except Exception as e:
        print(f"❌ Failed to send email: {e}")  # DEBUG PRINT
        logger.error(f"Failed to send email: {e}")
        return False

    print(f"✅ Email sent successfully to {recipient_list}!") # DEBUG PRINT
    return True
