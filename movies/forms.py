from django import forms
from .models import Client, Order


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['first_name', 'last_name', 'username', 'email', 'password', 'address']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name':forms.TextInput(attrs={'class': 'form-control'}),
            'email':forms.TextInput(attrs={'class': 'form-control'}),
            'password':forms.TextInput(attrs={'class': 'form-control'}),
            'address':forms.TextInput(attrs={'class': 'form-control'})
        }

class SignUpForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['first_name', 'last_name', 'username', 'email', 'password']
        widgets = {
            'username' : forms.TextInput(attrs={'class':'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.TextInput(attrs={'class': 'form-control'}),
            'password': forms.TextInput(attrs={'class': 'form-control'}),
            # 'address': forms.TextInput(attrs={'class': 'form-control'})
        }

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'email', 'shipping_address', 'movies', 'client', 'total_price']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.TextInput(attrs={'class': 'form-control'}),
            'shipping_address': forms.TextInput(attrs={'class': 'form-control'})
        }
        exclude = ['movies', 'client', 'total_price']