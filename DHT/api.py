from .models import Dht11, Ticket, AuditLog, DhtSettings
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
        
        # Get Settings
        settings_obj = DhtSettings.objects.first()
        if not settings_obj:
            settings_obj = DhtSettings.objects.create(temp_min=2.0, temp_max=8.0)
            
        t_min = settings_obj.temp_min
        t_max = settings_obj.temp_max
        
        # Alert Logic: Temp < Min or > Max
        if temp < t_min or temp > t_max:
            # Calculate Deviation
            deviation = 0
            if temp < t_min:
                deviation = t_min - temp
            elif temp > t_max:
                deviation = temp - t_max
            
            # Determine Severity
            severity = 'WARNING'
            if deviation >= 5:
                severity = 'SEVERE'
            elif deviation >= 2:
                severity = 'CRITICAL'
            
            msg = f"⚠️ Alert! Temperature: {temp}°C (Range: {t_min}-{t_max}°C) - Level: {severity}"
            
            # Check for existing OPEN ticket
            open_ticket = Ticket.objects.filter(status='OPEN').first()
            
            if not open_ticket:
                # Create Level 1 Ticket (Operator)
                ticket = Ticket.objects.create(
                    dht_record=instance,
                    status='OPEN',
                    level='OPERATOR',
                    severity=severity,
                    description=msg
                )
                AuditLog.objects.create(action="Ticket Created", details=f"Ticket #{ticket.id} ({severity}) created for {temp}°C")
                
                # Notify Operator (Initial Alert)
                send_telegram_message(f"🚨 {severity} ALERT: {msg} - Ticket #{ticket.id} (Operator)")
                contact = getattr(settings, 'OPERATOR_CONTACT', {})
                if contact.get('email'):
                    send_alert_email("🔥 New Alert (Operator)", msg, [contact['email']])

            else:
                # Update Severity if new reading is worse
                if (severity == 'SEVERE' and open_ticket.severity != 'SEVERE') or \
                   (severity == 'CRITICAL' and open_ticket.severity == 'WARNING'):
                    open_ticket.severity = severity
                    open_ticket.save()
                    msg_upd = f"🚨 Escalation Severity to {severity}: Ticket #{open_ticket.id}"
                    AuditLog.objects.create(action="Severity Update", details=msg_upd)
                    send_telegram_message(msg_upd)
                
                # Alert persists - Log it
                AuditLog.objects.create(action="Alert Persists", details=f"Existing ticket #{open_ticket.id} for {temp}°C")
                
                # Count Persistent Alerts
                persist_count = AuditLog.objects.filter(
                    action="Alert Persists", 
                    details__contains=f"Ticket #{open_ticket.id}"
                ).count()
                
                print(f"🔢 DEBUG: Ticket #{open_ticket.id} has {persist_count} persistent alerts. Level: {open_ticket.level}")
                
                # Escalation Logic:
                # 1. 2nd Alert (Persist Count >= 1) -> Escalate to CHIEF
                # 2. 2 Alerts in Chief (Persist Count >= 3) -> Escalate to MANAGER
                
                escalated = False

                if open_ticket.level == 'OPERATOR' and persist_count >= 1:
                    open_ticket.level = 'CHIEF'
                    open_ticket.save()
                    msg_esc = f"🚨 Escalation! Ticket #{open_ticket.id} upgraded to CHIEF level (2nd Alert)."
                    AuditLog.objects.create(action="Escalation", details=msg_esc)
                    
                    # Notify Chief
                    contact = getattr(settings, 'CHIEF_CONTACT', {})
                    if contact.get('email'):
                        send_alert_email("Escalation Alert (Chief)", msg + "\n" + msg_esc, [contact['email']])
                    send_telegram_message(msg_esc)
                    escalated = True
                    
                elif open_ticket.level == 'CHIEF' and persist_count >= 3:
                    open_ticket.level = 'MANAGER'
                    open_ticket.save()
                    msg_esc = f"🚨🔥 Escalation! Ticket #{open_ticket.id} upgraded to MANAGER level (4th Alert)."
                    AuditLog.objects.create(action="Escalation", details=msg_esc)
                    
                    # Notify Manager
                    contact = getattr(settings, 'MANAGER_CONTACT', {})
                    if contact.get('email'):
                        send_alert_email("Escalation Alert (Manager)", msg + "\n" + msg_esc, [contact['email']])
                    send_telegram_message(msg_esc)
                    escalated = True
                
                # If NOT just escalated, enforce sending email to current owner
                if not escalated:
                    # Determine current owner
                    target_role = open_ticket.level # OPERATOR, CHIEF, MANAGER
                    contact = {}
                    if target_role == 'OPERATOR':
                        contact = getattr(settings, 'OPERATOR_CONTACT', {})
                    elif target_role == 'CHIEF':
                        contact = getattr(settings, 'CHIEF_CONTACT', {})
                    elif target_role == 'MANAGER':
                        contact = getattr(settings, 'MANAGER_CONTACT', {})
                    
                    if contact.get('email'):
                        print(f"📧 Sending persistent alert email to {target_role}: {contact['email']}")
                        send_alert_email(f"⚠️ Warning: Temperature Alert ({target_role})", msg, [contact['email']])
                    
                    # Optional: Also notify Telegram
                    # send_telegram_message(f"Persistent Alert ({target_role}): {msg}")

        # Normal Temperature Logic (t_min <= temp <= t_max)
        else:
            # Check for any OPEN ticket to close it automatically
            open_ticket = Ticket.objects.filter(status='OPEN').first()
            
            if open_ticket:
                open_ticket.status = 'CLOSED'
                # Optional: You could assign a 'System' user or leave resolved_by null
                open_ticket.save()
                
                msg_resolve = f"✅ System Auto-Resolution: Temperature Stabilized at {temp}°C. Ticket #{open_ticket.id} Closed."
                AuditLog.objects.create(action="Ticket Closed (Auto)", details=msg_resolve)
                
                # Notify Operator/Chief/Manager about resolution
                send_telegram_message(msg_resolve)
                print(msg_resolve)