from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = (('Admin', 'Admin'), ('Vet', 'Vet'))
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='Admin')
    groups = models.ManyToManyField('auth.Group', related_name='dairy_user_groups', blank=True)
    user_permissions = models.ManyToManyField('auth.Permission', related_name='dairy_user_perms', blank=True)

class Cattle(models.Model):
    tag_id = models.CharField(max_length=50, unique=True)
    breed = models.CharField(max_length=100)
    birth_date = models.DateField()
    health_status = models.CharField(max_length=100, default='Healthy')
    def __str__(self): return self.tag_id

class MilkProduction(models.Model):
    cattle = models.ForeignKey(Cattle, on_delete=models.CASCADE)
    date = models.DateField()
    quantity_liters = models.DecimalField(max_digits=5, decimal_places=2)

class FeedingRecord(models.Model):
    cattle = models.ForeignKey(Cattle, on_delete=models.CASCADE)
    feed_type = models.CharField(max_length=100)
    quantity_kg = models.DecimalField(max_digits=5, decimal_places=2)
    feed_time = models.DateTimeField(auto_now_add=True)

class HealthRecord(models.Model):
    cattle = models.ForeignKey(Cattle, on_delete=models.CASCADE)
    checkup_date = models.DateField()
    diagnosis = models.TextField()
    treatment = models.TextField()
    vet_assigned = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, limit_choices_to={'role': 'Vet'})

class Inventory(models.Model):
    item_name = models.CharField(max_length=100)
    quantity = models.IntegerField()
    unit = models.CharField(max_length=20)

class VetHealthRecord(models.Model):
    STATUS_CHOICES = [('pending','Pending'), ('completed','Completed')]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    cattle = models.ForeignKey(Cattle, on_delete=models.CASCADE)
    vet_assigned = models.ForeignKey(User, on_delete=models.CASCADE)
    visit_date = models.DateField(auto_now_add=True)
    due_date = models.DateField(null=True, blank=True)
    note = models.TextField()
    
    def is_overdue(self):
        from datetime import date
        if self.due_date and self.status == 'pending':
            return self.due_date < date.today()
        return False

class Treatment(models.Model):
    cattle = models.ForeignKey(Cattle, on_delete=models.CASCADE, related_name='treatments')
    treatment_details = models.TextField()
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Treatment for {self.cattle.tag_id} on {self.date}"
    
class Vaccination(models.Model):
    cattle = models.ForeignKey(Cattle, on_delete=models.CASCADE, related_name='vaccinations')
    vaccine_name = models.CharField(max_length=100)
    date = models.DateField()
    next_due_date = models.DateField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    administered_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)  # Make sure this exists

    def __str__(self):
        status = "Completed" if self.is_completed else f"Next due: {self.next_due_date}"
        return f"{self.vaccine_name} - {self.cattle.tag_id} ({status})"