from django import forms
from core.models import CreditCard

class CreditCardForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={"placeholder":"Card Holder Name"}))
    number = forms.IntegerField(widget=forms.NumberInput(attrs={"placeholder":"Card Number"}))
    month = forms.IntegerField(widget=forms.NumberInput(attrs={"placeholder":"Expiry Month"}))
    year = forms.IntegerField(widget=forms.NumberInput(attrs={"placeholder":"Expiry Month"}))
    cvc = forms.IntegerField(widget=forms.NumberInput(attrs={"placeholder":"CVC"}))

    class Meta:
        model = CreditCard
        fields = ['name', 'number', 'month', 'year', 'cvc', 'card_type']

class AmountForm(forms.ModelForm):
    amount = forms.IntegerField(widget=forms.NumberInput(attrs={"placeholder":"$30"}))
    
    class Meta:
        model = CreditCard
        fields = ['amount']
