from django.urls import path
from . import views

urlpatterns = [
    # Login / Logout
    path('', views.login_view, name='login_view'),
    path('logout/', views.logout_view, name='logout_view'),

    # Admin URLs
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('add-cattle/', views.add_cattle, name='add_cattle'),
    path('add-inventory/', views.add_inventory, name='add_inventory'),
    path('log-milk/', views.log_milk, name='log_milk'),

    # Vet URLs - NAMES MUST MATCH TEMPLATE
    path('vet-dashboard/', views.vet_dashboard, name='vet_dashboard'),
    path('add-health-record/', views.add_health_record, name='add_health_record'),
    path('add-vaccination/', views.add_vaccination, name='add_vaccination'),  # Note: name is 'add_vaccination'
    path('cattle-list/', views.cattle_list, name='cattle_list'),
    path('cattle-health-history/<int:cattle_id>/', views.cattle_health_history, name='cattle_health_history'),
    path('mark-completed/<int:record_id>/', views.mark_completed, name='mark_completed'),
]