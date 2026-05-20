from django import forms
from .models import Opportunity

class OpportunityForm(forms.ModelForm):
    class Meta:
        model = Opportunity
        fields = [
            'title',
            'company',
            'description',
            'location',
            'deadline',
            'type'
        ]
