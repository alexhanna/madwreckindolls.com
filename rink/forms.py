from django import forms

class ProcessForm(forms.Form):
    pass

class AutopayForm(forms.Form):
    autobill = forms.IntegerField(
        required = True,
    )

class PaymentForm(forms.Form):

    stripe_token = forms.CharField(
        max_length = 32,
        required = True,
    )

    autobill = forms.BooleanField(
        required = True,
    )
