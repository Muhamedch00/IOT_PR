from django.urls import path
from . import views
from . import api
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Auth
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),

    # API endpoint to get all DHT11 data
    path("api/", api.Dlist, name='json'),  # GET request to get all data

    # API endpoint to create DHT11 data (POST request)
    path("api/post", api.Dhtviews.as_view(), name='json'),  # POST request to add data
    path("api/data", views.get_history, name='json_data'),

    # Dashboard page (default page)
    path("", views.dashboard, name="dashboard"),

    # Endpoint to provide the latest sensor data as JSON (for real-time updates)
    path("latest/", views.latest_json, name="latest_json"),

    # Graph pages for temperature and humidity
    path('graph-temp/', views.graph_temp, name='graph_temp'),
    path('graph-hum/', views.graph_hum, name='graph_hum'),
    
    # New Pages
    path('history/', views.historical_graph_view, name='history'),
    path('measurements/', views.measures_list_view, name='measurements'),
    path('logs/', views.audit_log_view, name='logs'),
    
    # Admin
    path('admin-users/', views.admin_users_view, name='admin_users'),
    path('admin-users/create/', views.admin_create_user, name='admin_create'),
    path('admin-users/delete/<int:user_id>/', views.admin_delete_user, name='admin_delete'),
    path('admin-users/settings/', views.admin_update_settings, name='admin_settings'),

    # Ticketing & Export
    path('tickets/', views.ticket_list_view, name='tickets'),
    path('tickets/close/<int:ticket_id>/', views.close_ticket, name='close_ticket'),
    path('export-csv/', views.export_csv, name='export_csv'),
    path('export-measures-csv/', views.export_measures_csv, name='export_measures_csv'),
]
