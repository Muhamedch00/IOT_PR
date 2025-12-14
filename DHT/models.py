
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
    
    dht_record = models.ForeignKey(Dht11, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='OPEN')
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='OPERATOR')
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

