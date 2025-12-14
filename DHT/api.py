from .models import Dht11, Ticket, AuditLog
from .serializers import DHT11serialize
from rest_framework.decorators import api_view
from rest_framework import status, generics
from rest_framework.response import Response
from django.conf import settings
from .utils import send_alert_email, send_telegram_message, send_whatsapp_message
import rest_framework

@api_view(['GET'])
def Dlist(request):
    all_data = Dht11.objects.all()
    data = DHT11serialize(all_data, many=True).data
    return Response({'data': data})

class Dhtviews(generics.CreateAPIView):
    queryset = Dht11.objects.all()
    serializer_class = DHT11serialize
    
    def perform_create(self, serializer):
        instance = serializer.save()
        temp = instance.temp
        
        # Alert Logic: Temp < 2 or > 8
        if temp < 2 or temp > 8:
            msg = f"⚠️ Alert! Temperature: {temp}°C (Range: 2-8°C)"
            
            # Check for existing OPEN ticket
            open_ticket = Ticket.objects.filter(status='OPEN').first()
            
            if not open_ticket:
                # Create Level 1 Ticket (Operator)
                ticket = Ticket.objects.create(
                    dht_record=instance,
                    status='OPEN',
                    level='OPERATOR',
                    description=msg
                )
                AuditLog.objects.create(action="Ticket Created", details=f"Ticket #{ticket.id} created for {temp}°C")
                send_telegram_message(f"{msg} - Ticket #{ticket.id} assigned to OPERATOR")
            else:
                # Alert persists
                AuditLog.objects.create(action="Alert Persists", details=f"Existing ticket #{open_ticket.id} for {temp}°C")
                
                # ESCALATION LOGIC: Count-based (Based on "3 consecutive alerts" rule)
                # We count how many "Alert Persists" logs exist for this ticket
                # Note: This is a simple implementation. In production, exact consecutive checks might be stricter.
                
                persist_count = AuditLog.objects.filter(
                    action="Alert Persists", 
                    details__contains=f"Ticket #{open_ticket.id}"
                ).count()
                
                print(f"🔢 DEBUG: Ticket #{open_ticket.id} has {persist_count} persistent alerts. Level: {open_ticket.level}")

                # Level 1 -> Level 2 (Chef) after 3 alerts
                if open_ticket.level == 'OPERATOR' and persist_count >= 3:
                    open_ticket.level = 'CHIEF'
                    open_ticket.save()
                    msg_esc = f"🚨 Escalation! Ticket #{open_ticket.id} upgraded to CHIEF level (3 persistent alerts)."
                    AuditLog.objects.create(action="Escalation", details=msg_esc)
                    
                    # Notify Chief
                    contact = getattr(settings, 'CHIEF_CONTACT', {})
                    if contact.get('email'):
                        send_alert_email("Escalation Alert (Chief)", msg_esc, [contact['email']])
                    send_telegram_message(msg_esc)
                    
                # Level 2 -> Level 3 (Manager) after 3 MORE alerts (Total 6)
                elif open_ticket.level == 'CHIEF' and persist_count >= 6:
                    open_ticket.level = 'MANAGER'
                    open_ticket.save()
                    msg_esc = f"🚨🔥 Escalation! Ticket #{open_ticket.id} upgraded to MANAGER level (6 persistent alerts)."
                    AuditLog.objects.create(action="Escalation", details=msg_esc)
                    
                    # Notify Manager
                    contact = getattr(settings, 'MANAGER_CONTACT', {})
                    if contact.get('email'):
                        send_alert_email("Escalation Alert (Manager)", msg_esc, [contact['email']])
                    send_telegram_message(msg_esc)

            # ALWAYS Send Alerts to Operator (moved outside the check)
            contact = getattr(settings, 'OPERATOR_CONTACT', {})
            
            if contact.get('email'):
                print(f"📧 Sending email to {contact['email']}")
                send_alert_email("⚠️ Warning: Temperature Alert", msg, [contact['email']])
            
            if contact.get('phone'):
                # WhatsApp (Optional: uncomment if needed)
                send_whatsapp_message(msg, contact['phone'])