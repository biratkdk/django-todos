from django import forms
from django.contrib.auth import authenticate

from .models import User


class RegistrationForm(forms.ModelForm):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={"placeholder": "Username"}),
        error_messages={"required": "Username is required"},
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"placeholder": "E-mail address"}),
        error_messages={
            "required": "Email is required",
            "invalid": "Enter a valid email address",
        },
    )
    password = forms.CharField(
        strip=False,
        widget=forms.PasswordInput(attrs={"placeholder": "Password"}),
        error_messages={"required": "Password is required"},
    )
    password2 = forms.CharField(
        strip=False,
        label="Repeat password",
        widget=forms.PasswordInput(attrs={"placeholder": "Repeat Password"}),
        error_messages={"required": "Repeat password is required"},
    )

    class Meta:
        model = User
        fields = ["username", "email"]

    def clean_username(self):
        username = self.cleaned_data["username"].strip()
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username is taken, choose another one")
        return username

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email is taken, choose another one")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password") or ""
        password2 = cleaned_data.get("password2") or ""

        if password and len(password) < 6:
            self.add_error("password", "Password should be at least 6 characters")

        if password and password2 and password != password2:
            self.add_error("password2", "Password mismatch")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data["username"]
        user.email = self.cleaned_data["email"]
        user.set_password(self.cleaned_data["password"])

        if commit:
            user.save()

        return user


class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={"placeholder": "Username"}),
        error_messages={"required": "Username is required"},
    )
    password = forms.CharField(
        strip=False,
        widget=forms.PasswordInput(attrs={"placeholder": "Password"}),
        error_messages={"required": "Password is required"},
    )

    def __init__(self, *args, request=None, **kwargs):
        self.request = request
        self.user = None
        super().__init__(*args, **kwargs)

    def clean_username(self):
        return self.cleaned_data["username"].strip()

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        password = cleaned_data.get("password")

        if not username or not password:
            return cleaned_data

        user = authenticate(self.request, username=username, password=password)

        if not user:
            raise forms.ValidationError("Invalid credentials, try again")

        if not user.is_email_verified:
            raise forms.ValidationError(
                "Email is not verified, please check your email inbox"
            )

        self.user = user
        return cleaned_data

    def get_user(self):
        return self.user
