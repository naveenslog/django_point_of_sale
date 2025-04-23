from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from tenant.models import TenantUser

from django import forms
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.db import connection
from tenant.models import TenantUser  # your custom user model

class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            "placeholder": "Username",
            "class": "form-control form-control-user"
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "placeholder": "Password",
            "class": "form-control form-control-user"
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        password = cleaned_data.get("password")

        if username and password:
            user = authenticate(username=username, password=password)
            if user is None:
                raise ValidationError("Invalid username or password")

            current_tenant = connection.tenant

            if hasattr(user, "tenant") and user.tenant_id != current_tenant.id:
                raise ValidationError("You are not authorized to log in to this tenant.")

            cleaned_data["user"] = user  # for use in the view

        return cleaned_data



class SignUpForm(UserCreationForm):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Username",
                "class": "form-control"
            }
        ))
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "placeholder": "Email",
                "class": "form-control"
            }
        ))
    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password",
                "class": "form-control"
            }
        ))
    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password confirmation",
                "class": "form-control"
            }
        ))

    class Meta:
        model = TenantUser
        fields = ('username', 'email', 'password1', 'password2')
