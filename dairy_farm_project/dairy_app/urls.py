from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login_view'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('vet-dashboard/', views.vet_dashboard, name='vet_dashboard'),
    path('add-cattle/', views.add_cattle, name='add_cattle'),
    path('logout/', views.logout_view, name='logout_view'),
    path('add-inventory/', views.add_inventory, name='add_inventory'),
    path('log-milk/', views.log_milk, name='log_milk'),
]