from django.shortcuts import render, redirect
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from .models import Cattle, MilkProduction, Inventory, HealthRecord
from .forms import CattleForm, InventoryForm, MilkProductionForm
from datetime import date

# 1. Login Logic
def login_view(request):
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        user = auth.authenticate(username=u, password=p)
        if user is not None:
            auth.login(request, user)
            return redirect('admin_dashboard' if user.role == 'Admin' else 'vet_dashboard')
        else:
            return render(request, 'login.html', {'error': 'Invalid Credentials'})
    return render(request, 'login.html')

# 2. Admin Dashboard (Calculates live stats for the cards)
@login_required
def admin_dashboard(request):
    if request.user.role != 'Admin':
        return redirect('vet_dashboard')
    
    # Calculate sum of milk for TODAY only
    today_records = MilkProduction.objects.filter(date=date.today())
    milk_sum = sum(record.quantity_liters for record in today_records)

    context = {
        'total_cattle': Cattle.objects.count(),
        'inventory_items': Inventory.objects.all(),
        'milk_today': milk_sum,
    }
    return render(request, 'admin_dashboard.html', context)

# 3. New: Add Cattle through the website
@login_required
def add_cattle(request):
    if request.user.role != 'Admin':
        return redirect('vet_dashboard')
    form = CattleForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('admin_dashboard')
    return render(request, 'add_cattle.html', {'form': form})

# 4. New: Add Inventory through the website
@login_required
def add_inventory(request):
    if request.user.role != 'Admin':
        return redirect('vet_dashboard')
    form = InventoryForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('admin_dashboard')
    return render(request, 'add_inventory.html', {'form': form})

# 5. New: Log Milk Production through the website
@login_required
def log_milk(request):
    if request.user.role != 'Admin':
        return redirect('vet_dashboard')
    form = MilkProductionForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('admin_dashboard')
    return render(request, 'log_milk.html', {'form': form})

# 6. Vet Dashboard
@login_required
def vet_dashboard(request):
    context = {
        'pending_checkups': HealthRecord.objects.filter(vet_assigned=request.user).count(),
    }
    return render(request, 'vet_dashboard.html', context)

# 7. Logout Logic
def logout_view(request):
    auth.logout(request)
    return redirect('login_view')