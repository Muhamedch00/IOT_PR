from django.contrib import admin
from DHT import models

admin.site.register(models.Dht11)
admin.site.register(models.Ticket)
admin.site.register(models.AuditLog)