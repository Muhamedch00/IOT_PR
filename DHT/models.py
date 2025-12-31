
from django.db import models

from django.contrib.auth.models import User

class Dht11(models.Model):
    temp = models.FloatField(null=True)
    hum = models.FloatField(null=True)
    dt = models.DateTimeField(auto_now_add=True,null=True)
    
    def __str__(self):
        return f"Temp: {self.temp}, Hum: {self.hum}"

class Ticket(models.Model):
    STATUS_CHOICES = (
        ('OPEN', 'Open'),
        ('ASSIGNED', 'Assigned'),
        ('IN_PROGRESS', 'In Progress'),
        ('CLOSED', 'Closed'),
    )
    LEVEL_CHOICES = (
        ('OPERATOR', 'Operator'),
        ('CHIEF', 'Chief'),
        ('MANAGER', 'Manager'),
    )
    
    SEVERITY_CHOICES = (
        ('WARNING', 'Warning'),
        ('CRITICAL', 'Critical'),
        ('SEVERE', 'Severe'),
    )
    
    dht_record = models.ForeignKey(Dht11, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='OPEN')
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='OPERATOR')
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='WARNING')
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f"Ticket #{self.id} - {self.status} ({self.level})"

class AuditLog(models.Model):
    action = models.CharField(max_length=100)
    details = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.action} at {self.timestamp}"

class IncidentComment(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Comment by {self.user.username} on Ticket #{self.ticket.id}"

class DhtSettings(models.Model):
    temp_min = models.FloatField(default=2.0)
    temp_max = models.FloatField(default=8.0)
    
    def __str__(self):
        return f"Settings (Min: {self.temp_min}, Max: {self.temp_max})"

    def save(self, *args, **kwargs):
        # Singleton logic: ensure only one instance exists
        if not self.pk and DhtSettings.objects.exists():
             # Update the existing one instead of creating new
             existing = DhtSettings.objects.first()
             existing.temp_min = self.temp_min
             existing.temp_max = self.temp_max
             return existing.save()
        return super(DhtSettings, self).save(*args, **kwargs)

