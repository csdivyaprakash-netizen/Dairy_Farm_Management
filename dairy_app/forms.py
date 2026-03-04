from django import forms
from .models import Cattle, Inventory, MilkProduction, HealthRecord, VetHealthRecord, Treatment, Vaccination

class CattleForm(forms.ModelForm):
    class Meta:
        model = Cattle
        fields = ['tag_id', 'breed', 'birth_date', 'health_status']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

class InventoryForm(forms.ModelForm):
    class Meta:
        model = Inventory
        fields = ['item_name', 'quantity', 'unit']
        widgets = {
            'item_name': forms.TextInput(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'unit': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. kg, Liters'}),
        }

class MilkProductionForm(forms.ModelForm):
    class Meta:
        model = MilkProduction
        fields = ['cattle', 'date', 'quantity_liters']
        widgets = {
            'cattle': forms.Select(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'quantity_liters': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class VetHealthRecordForm(forms.ModelForm):
    class Meta:
        model = VetHealthRecord
        fields = ['cattle', 'note']
        widgets = {
            'note': forms.Textarea(attrs={'rows': 4, 'cols': 40, 'placeholder': 'Enter health note here...'}),
        }

class TreatmentForm(forms.ModelForm):
    class Meta:
        model = Treatment
        fields = ['cattle', 'treatment_details']
        widgets = {
            'treatment_details': forms.Textarea(attrs={'rows':4, 'cols':40, 'placeholder':'Enter treatment details...'})
        }

class VaccinationForm(forms.ModelForm):
    next_due_days = forms.IntegerField(
        label="Next vaccination due in (days)",
        min_value=0,
        help_text="Enter 0 if this is the final shot. Enter any positive number for next due date.",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 45'})
    )
    
    class Meta:
        model = Vaccination
        fields = ['cattle', 'vaccine_name', 'date', 'next_due_days']
        widgets = {
            'cattle': forms.Select(attrs={'class': 'form-control'}),
            'vaccine_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. FMD Vaccine'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }
    
    def clean_next_due_days(self):
        days = self.cleaned_data['next_due_days']
        if days < 0:
            raise forms.ValidationError("Days cannot be negative.")
        return days
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        days = self.cleaned_data['next_due_days']
        
        if days == 0:
            instance.is_completed = True
            instance.next_due_date = None
        else:
            instance.is_completed = False
            from datetime import timedelta
            instance.next_due_date = instance.date + timedelta(days=days)
        
        if commit:
            instance.save()
        return instance