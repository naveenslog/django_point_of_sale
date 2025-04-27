# inventory/forms.py
from django import forms
from .models import RawMaterial, Ledger, Worker

class RawMaterialForm(forms.ModelForm):
    class Meta:
        model = RawMaterial
        fields = ['name', 'description', 'unit_of_measurement']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Ledger
        fields = ['worker', 'material', 'quantity', 'transaction_type', 'purpose']
        widgets = {
            'purpose': forms.Textarea(attrs={'rows': 2}),
            'transaction_type': forms.RadioSelect(choices=Ledger.TRANSACTION_TYPES),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['worker'].queryset = Worker.objects.all()
        self.fields['material'].queryset = RawMaterial.objects.all()

class WorkerForm(forms.ModelForm):
    class Meta:
        model = Worker
        fields = ['user', 'role']