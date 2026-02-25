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
    feed_time = models.DateTimeField(auto_now_add=True) # Corrected variable name

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