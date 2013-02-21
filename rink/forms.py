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


class AdminSkaterStatusForm(forms.Form):
    status = forms.CharField(
        max_length=32,
        required = True,
    )

class AdminSkaterPaymentForm(forms.Form):
    method = forms.CharField(
        max_length=32,
        required=True,
    )

    notes = forms.CharField(
        max_length=128,
        required=False,
    )

    amount = forms.DecimalField(
        decimal_places=2,
        required=True,
    )
