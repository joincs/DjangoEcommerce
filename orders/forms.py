from django import forms
from .models import UserCheckout,UserAddress
from django.contrib.auth import get_user_model

User = get_user_model()

class GuestCheckoutForm(forms.Form):
    email = forms.EmailField()
    email2 = forms.EmailField(label='Confirm Email')

    def clean_email2(self):
        email = self.cleaned_data.get("email")
        email2 = self.cleaned_data.get("email2")

        if email == email2:
            user_exists = User.objects.filter(email=email).count()
            if user_exists != 0:
                raise forms.ValidationError("This user already exists, Please login instead.")
            return email2
        else:
            raise forms.ValidationError("Please confirm emails are same")


class AdressForm(forms.Form):
    billing_address  = forms.ModelChoiceField(
        queryset=UserAddress.objects.filter(bill_type="billing"),
        widget=forms.RadioSelect,
        empty_label=None
        )
    shipping_address = forms.ModelChoiceField(
        queryset=UserAddress.objects.filter(bill_type="shipping"),
        widget=forms.RadioSelect,
        empty_label=None
        )


class UserAddressForm(forms.ModelForm):
    class Meta:
        model  = UserAddress
        fields = ['street','city','country','zipcode','bill_type']

