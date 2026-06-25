from django import forms
from .models import CourtCase, HearingLog

class LogDecisionForm(forms.ModelForm):
    class Meta:
        model = HearingLog
        fields = ['hearing_date', 'outcome', 'bail_amount', 'bail_conditions', 'notes']
        widgets = {
            'hearing_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'outcome': forms.RadioSelect,
            'bail_conditions': forms.Textarea(attrs={'rows': 3}),
            'notes': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'outcome' in self.fields:
            self.fields['outcome'].choices = [c for c in self.fields['outcome'].choices if c[0]]
        if not self.initial.get('hearing_date') and not self.data:
            from django.utils import timezone
            self.initial['hearing_date'] = timezone.now().strftime('%Y-%m-%dT%H:%M')

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


class ScheduleHearingForm(forms.Form):
    case = forms.ModelChoiceField(
        queryset=CourtCase.objects.none(),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    next_court_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-input'}, format='%Y-%m-%dT%H:%M')
    )

    def __init__(self, *args, **kwargs):
        court = kwargs.pop('court', None)
        super().__init__(*args, **kwargs)
        if court is not None:
            self.fields['case'].queryset = CourtCase.objects.filter(court=court, status='ONGOING')
        if not self.initial.get('next_court_date') and not self.data:
            from django.utils import timezone
            self.initial['next_court_date'] = timezone.now().strftime('%Y-%m-%dT%H:%M')

