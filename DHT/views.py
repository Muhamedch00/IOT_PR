# views.py


from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from .models import Dht11, AuditLog, Ticket, IncidentComment, DhtSettings
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
import csv

@login_required
def dashboard(request):
    # Determine Role
    # Incident Management
    open_ticket = Ticket.objects.filter(status='OPEN').first()
    comments = []
    duration = None
    
    if open_ticket:
        comments = open_ticket.comments.all().order_by('-created_at')
        duration = timezone.now() - open_ticket.created_at
        
        # Handle New Comment
        if request.method == "POST" and 'comment' in request.POST:
            text = request.POST['comment']
            IncidentComment.objects.create(ticket=open_ticket, user=request.user, text=text)
            return redirect('dashboard')
        
    return render(request, "dashboard.html", {
        'incident': open_ticket,
        'comments': comments,
        'duration': duration
    })

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
def measures_list_view(request):
    measures = Dht11.objects.all().order_by('-dt')
    return render(request, "measure_list.html", {'measures': measures})

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

def export_measures_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="mesures.csv"'

    writer = csv.writer(response)
    writer.writerow(['Timestamp', 'Température (°C)', 'Humidité (%)'])

    measures = Dht11.objects.all().order_by('-dt')
    for measure in measures:
        writer.writerow([measure.dt, measure.temp, measure.hum])

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
    import datetime
    from django.utils import timezone
    
    # Base query
    queryset = Dht11.objects.all().order_by('-dt')
    
    # 1. Date Filter
    date_str = request.GET.get('date')
    if date_str:
        try:
            target_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
            # Filter by specific day (start of day to end of day logic usually handled by __date lookup)
            queryset = queryset.filter(dt__date=target_date)
        except ValueError:
            pass # Invalid date format, ignore
            
    # 2. Range Filter (if no specific date)
    elif request.GET.get('range'):
        range_val = request.GET.get('range')
        now = timezone.now()
        
        if range_val == 'month':
             start_date = now - datetime.timedelta(days=30)
             queryset = queryset.filter(dt__gte=start_date)
        elif range_val == '90days':
             start_date = now - datetime.timedelta(days=90)
             queryset = queryset.filter(dt__gte=start_date)
        # Add more ranges here if needed
        
    else:
        # Default behavior: Last 20 measures if no filter
        queryset = queryset[:20]

    # If it's a slice (list), use it. If it's a queryset, we might want to limit the points for performance 
    # if the range is huge, but for now let's return all points in the range.
    # Note: If 'queryset' was sliced above ([:20]), it's a list/queryset slice.
    
    measures = list(queryset) 
    
    # Sort back to chronological order for the graph (Oldest -> Newest)
    # The queryset was ordered by '-dt' (Newest -> Oldest) to get the "latest" ones easily or "limit" them.
    # So we reverse the list for the Chart.
    measures.sort(key=lambda x: x.dt)

    data = {
        'labels': [m.dt.strftime('%d-%m-%Y %H:%M:%S') for m in measures],
        'temps': [m.temp for m in measures],
        'hums': [m.hum for m in measures]
    }
    return JsonResponse(data)


# ... Admin Views ...

from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import user_passes_test

def is_admin(user):
    return user.is_superuser

@user_passes_test(is_admin)
def admin_users_view(request):
    users = User.objects.all()
    # Get or Create Settings
    settings_obj = DhtSettings.objects.first()
    if not settings_obj:
        settings_obj = DhtSettings.objects.create(temp_min=2.0, temp_max=8.0)
        
    return render(request, "admin_users.html", {'users': users, 'settings': settings_obj})

@user_passes_test(is_admin)
def admin_update_settings(request):
    if request.method == "POST":
        try:
            t_min = float(request.POST['temp_min'])
            t_max = float(request.POST['temp_max'])
            
            settings_obj = DhtSettings.objects.first()
            if not settings_obj:
                settings_obj = DhtSettings.objects.create(temp_min=t_min, temp_max=t_max)
            else:
                settings_obj.temp_min = t_min
                settings_obj.temp_max = t_max
                settings_obj.save()
            
            AuditLog.objects.create(action="Settings Updated", details=f"Thresholds set to Min:{t_min}, Max:{t_max} by {request.user.username}")
        except ValueError:
            pass # Handle invalid input gracefully
            
    return redirect('admin_users')

@user_passes_test(is_admin)
def admin_create_user(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        role = request.POST['role']
        
        if User.objects.filter(username=username).exists():
             # Handle error (simple for now)
             return redirect('admin_users')
             
        user = User.objects.create_user(username=username, email=email, password=password)
        
        # Add to Group
        group, created = Group.objects.get_or_create(name=role)
        user.groups.add(group)
        user.save()
        
        AuditLog.objects.create(action="User Created", details=f"User {username} created as {role} by {request.user.username}")
        
    return redirect('admin_users')

@user_passes_test(is_admin)
def admin_delete_user(request, user_id):
    if request.method == "POST":
        user = get_object_or_404(User, id=user_id)
        if not user.is_superuser: # Prevent deleting admins via this simple UI
            username = user.username
            user.delete()
            AuditLog.objects.create(action="User Deleted", details=f"User {username} deleted by {request.user.username}")
    return redirect('admin_users')


