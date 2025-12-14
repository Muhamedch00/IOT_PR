# views.py


from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from .models import Dht11, AuditLog, Ticket
from django.contrib.auth.decorators import login_required # Added decorator
import csv

from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required

@login_required
def dashboard(request):
    # Determine Role
    role = "Utilisateur"
    if request.user.groups.filter(name='Manager').exists():
        role = "Manager"
    elif request.user.groups.filter(name='Chief').exists():
        role = "Chef"
    elif request.user.groups.filter(name='Operator').exists():
        role = "Opérateur"
        
    return render(request, "dashboard.html", {'role': role})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def historical_graph_view(request):
    return render(request, "historical_graph.html")

@login_required
def audit_log_view(request):
    logs = AuditLog.objects.all().order_by('-timestamp')
    return render(request, "audit_log.html", {'logs': logs})

@login_required
def ticket_list_view(request):
    tickets = Ticket.objects.all().order_by('-created_at')
    return render(request, "ticket_list.html", {'tickets': tickets})

@login_required
def close_ticket(request, ticket_id):
    if request.method == "POST":
        ticket = get_object_or_404(Ticket, id=ticket_id)
        ticket.status = 'CLOSED'
        ticket.resolved_by = request.user # Record who closed it
        ticket.save()
        AuditLog.objects.create(action="Ticket Closed", details=f"Ticket #{ticket.id} closed by {request.user.username}.")
    return redirect('tickets')

def export_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="audit_log.csv"'

    writer = csv.writer(response)
    writer.writerow(['Timestamp', 'Action', 'Details'])

    logs = AuditLog.objects.all().order_by('-timestamp')
    for log in logs:
        writer.writerow([log.timestamp, log.action, log.details])

    return response
def graph_temp(request):
    return render(request, "graph_temp.html")

# Graph for humidity
def graph_hum(request):
    return render(request, "graph_hum.html")

def latest_json(request):
    # Fournit la dernière mesure en JSON (sans passer par api.py)
    last = Dht11.objects.order_by('-dt').values('temp', 'hum', 'dt').first()
    if not last:
        return JsonResponse({"detail": "no data"}, status=404)
    return JsonResponse({
        "temperature": last["temp"],
        "humidity":    last["hum"],
        "timestamp":   last["dt"].isoformat()
    })

def get_history(request):
    # Get last 20 measures for graphs
    measures = Dht11.objects.order_by('-dt')[:20]
    data = {
        'labels': [m.dt.strftime('%d-%m-%Y %H:%M:%S') for m in measures][::-1],
        'temps': [m.temp for m in measures][::-1],
        'hums': [m.hum for m in measures][::-1]
    }
    return JsonResponse(data)


