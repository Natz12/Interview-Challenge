from django import forms
from portfolios.models import Investment

class DateFilterForm(forms.Form):
	start = forms.DateField()
	finish = forms.DateField()
	symbol = forms.CharField()