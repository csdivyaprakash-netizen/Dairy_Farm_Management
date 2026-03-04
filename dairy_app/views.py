from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import auth
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Cattle, MilkProduction, Inventory, HealthRecord, VetHealthRecord, Vaccination
from .forms import CattleForm, InventoryForm, MilkProductionForm, VetHealthRecordForm, TreatmentForm, VaccinationForm
from datetime import date, timedelta
from django.db.models import Q

# --- LOGIN LOGIC ---
def login_view(request):
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        user = auth.authenticate(username=u, password=p)
        if user is not None:
            auth.login(request, user)
            role = user.role.lower()
            if role == 'admin':
                return redirect('admin_dashboard')
            elif role == 'vet':
                return redirect('vet_dashboard')
            else:
                return redirect('login_view')
        else:
            return render(request, 'login.html', {'error': 'Invalid Credentials'})
    return render(request, 'login.html')

# --- ROLE CHECKS ---
def is_admin(user):
    return user.role.lower() == 'admin'

def is_vet(user):
    return user.role.lower() == 'vet'

# --- ADMIN VIEWS ---
@login_required
@user_passes_test(lambda u: u.role.lower() == 'admin')
def admin_dashboard(request):
    if request.user.role.lower() != 'admin':
        if request.user.role.lower() == 'vet':
            return redirect('vet_dashboard')
        return redirect('login_view')

    today_records = MilkProduction.objects.filter(date=date.today())
    milk_sum = sum(record.quantity_liters for record in today_records)
    context = {
        'total_cattle': Cattle.objects.count(),
        'inventory_items': Inventory.objects.all(),
        'milk_today': milk_sum,
    }
    return render(request, 'admin_app/admin_dashboard.html', context)

@login_required
@user_passes_test(is_admin)
def add_cattle(request):
    form = CattleForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Cattle added successfully!')
        return redirect('admin_dashboard')
    return render(request, 'admin_app/add_cattle.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def add_inventory(request):
    form = InventoryForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Inventory item added successfully!')
        return redirect('admin_dashboard')
    return render(request, 'admin_app/add_inventory.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def log_milk(request):
    form = MilkProductionForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Milk production logged successfully!')
        return redirect('admin_dashboard')
    return render(request, 'admin_app/log_milk.html', {'form': form})

# --- VET VIEWS ---
@login_required
@user_passes_test(lambda u: u.role.lower() == 'vet')
def vet_dashboard(request):
    today = date.today()
    
    # Get upcoming vaccinations (next 365 days)
    upcoming_vaccinations = Vaccination.objects.filter(
        is_completed=False,
        next_due_date__gte=today
    ).order_by('next_due_date')[:10]  # Show top 10 nearest
    
    # Calculate days until next vaccination for each
    for vax in upcoming_vaccinations:
        vax.days_until = (vax.next_due_date - today).days
    
    context = {
        'upcoming_vaccinations': upcoming_vaccinations,
        'today': today,
    }
    return render(request, 'vet_app/vet_dashboard.html', context)

@login_required
@user_passes_test(is_vet)
def add_health_record(request):
    if request.method == 'POST':
        form = VetHealthRecordForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            record.vet_assigned = request.user
            # Set default due date (30 days from now) if not provided
            if not record.due_date:
                record.due_date = date.today() + timedelta(days=30)
            record.save()
            messages.success(request, f'Health record for {record.cattle.tag_id} added successfully!')
            return redirect('vet_dashboard')
    else:
        form = VetHealthRecordForm()
    
    return render(request, 'vet_app/add_health_record.html', {'form': form})

@login_required
@user_passes_test(is_vet)
def mark_completed(request, record_id):
    record = get_object_or_404(VetHealthRecord, id=record_id, vet_assigned=request.user)
    record.status = 'completed'
    record.save()
    messages.success(request, f'Checkup for {record.cattle.tag_id} marked as completed!')
    return redirect('vet_dashboard')

@login_required
@user_passes_test(is_vet)
def cattle_list(request):
    """Display all cattle with their basic info and recent health records."""
    cattle = Cattle.objects.all().order_by('tag_id')
    
    # Get recent health records
    health_records = VetHealthRecord.objects.filter(
        vet_assigned=request.user
    ).order_by('-visit_date')[:50]
    
    # Get recent vaccinations
    vaccinations = Vaccination.objects.filter(
        administered_by=request.user
    ).order_by('-date')[:50]
    
    today = date.today()
    next_week = today + timedelta(days=7)
    
    return render(request, 'vet_app/cattle_list.html', {
        'cattle': cattle,
        'health_records': health_records,
        'vaccinations': vaccinations,
        'today': today,
        'next_week': next_week,
    })

@login_required
@user_passes_test(is_vet)
def cattle_health_history(request, cattle_id):
    """Display health history for a specific cattle."""
    cattle = get_object_or_404(Cattle, id=cattle_id)
    health_records = VetHealthRecord.objects.filter(
        cattle=cattle
    ).order_by('-visit_date')
    
    vaccinations = Vaccination.objects.filter(
        cattle=cattle
    ).order_by('-date')
    
    today = date.today()
    next_week = today + timedelta(days=7)
    
    return render(request, 'vet_app/cattle_health_history.html', {
        'cattle': cattle,
        'health_records': health_records,
        'vaccinations': vaccinations,
        'today': today,
        'next_week': next_week,
    })

# --- VACCINATION VIEW (New Page) ---
@login_required(login_url='login_view')  
@user_passes_test(is_vet, login_url='login_view')  
def add_vaccination(request):
    if request.method == 'POST':
        form = VaccinationForm(request.POST)
        if form.is_valid():
            vaccination = form.save(commit=False)
            vaccination.administered_by = request.user
            vaccination.save()
            
            if vaccination.is_completed:
                messages.success(request, f'✅ Vaccination completed for {vaccination.cattle.tag_id}!')
            else:
                messages.success(request, f'✅ Vaccination recorded for {vaccination.cattle.tag_id}. Next dose due: {vaccination.next_due_date}')
            
            return redirect('vet_dashboard')
    else:
        form = VaccinationForm()
    
    return render(request, 'vet_app/add_vaccination.html', {'form': form})

@login_required
@user_passes_test(is_vet)
def treatment_list(request):
    """View all treatments."""
    treatments = Treatment.objects.all().order_by('-date')[:100]
    return render(request, 'vet_app/treatment_list.html', {'treatments': treatments})

@login_required
@user_passes_test(is_vet)
def vaccination_list(request):
    """View all vaccinations."""
    today = date.today()
    
    upcoming = Vaccination.objects.filter(
        is_completed=False,
        next_due_date__gte=today
    ).order_by('next_due_date')
    
    overdue = Vaccination.objects.filter(
        is_completed=False,
        next_due_date__lt=today
    ).order_by('next_due_date')
    
    completed = Vaccination.objects.filter(
        is_completed=True
    ).order_by('-date')[:50]
    
    return render(request, 'vet_app/vaccination_list.html', {
        'upcoming': upcoming,
        'overdue': overdue,
        'completed': completed,
        'today': today,
    })

# --- LOGOUT ---
def logout_view(request):
    auth.logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login_view')