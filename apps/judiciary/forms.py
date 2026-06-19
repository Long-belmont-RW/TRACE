from django import forms
from .models import HearingLog

class LogDecisionForm(forms.ModelForm):
    class Meta:
        model = HearingLog
        fields = ['outcome', 'bail_amount', 'bail_conditions', 'notes']
        widgets = {
            'outcome': forms.RadioSelect,
            'bail_conditions': forms.Textarea(attrs={'rows': 3}),
            'notes': forms.Textarea(attrs={'rows': 4}),
        }

    def clean(self):
        cleaned_data = super().clean()
        outcome = cleaned_data.get("outcome")
        bail_amount = cleaned_data.get("bail_amount")
        bail_conditions = cleaned_data.get("bail_conditions")

        if outcome == 'BAIL_GRANTED':
            if not bail_amount:
                self.add_error('bail_amount', 'Bail amount is strictly required when bail is granted.')
            if not bail_conditions:
                self.add_error('bail_conditions', 'Bail conditions are strictly required when bail is granted.')

        return cleaned_data
