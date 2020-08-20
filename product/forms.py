from django import forms
from .models import Vairation
from django.forms.models import modelformset_factory

class VairationInventoryForm(forms.ModelForm):
    class Meta:
        model = Vairation
        fields = [
            'price',
            'sale_price',
            'inventory',
            'active'
        ]
    

VairationInventoryFormSet = modelformset_factory(Vairation, form=VairationInventoryForm, extra=0)