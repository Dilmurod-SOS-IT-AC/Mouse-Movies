from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class SingUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data["email"].lower()

        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("THis email is already taken.")

        return email