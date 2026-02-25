from django import forms
from .models import Cattle,Inventory,MilkProduction

class CattleForm(forms.ModelForm): # Corrected Class Name
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