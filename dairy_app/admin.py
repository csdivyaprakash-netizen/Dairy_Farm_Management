from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Cattle, MilkProduction, FeedingRecord, Inventory, HealthRecord

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (('Role Management', {'fields': ('role',)}),)
    list_display = ('username', 'role', 'is_staff')

@admin.register(FeedingRecord)
class FeedingRecordAdmin(admin.ModelAdmin):
    list_display = ('cattle', 'feed_type', 'quantity_kg', 'feed_time') # Matches model

admin.site.register(Cattle)
admin.site.register(MilkProduction)
admin.site.register(Inventory)
admin.site.register(HealthRecord)