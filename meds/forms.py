from django import forms
from django.core.exceptions import ValidationError
from .models import CustomUser, DoctorRequests

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)


    class Meta:
        model = CustomUser
        fields = ['full_name', 'email', 'phone', 'gender', 'dob', 'password']
  

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError("This email already exists")
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        if CustomUser.objects.filter(phone=phone).exists():
            raise ValidationError("This phone number already exists")
        return phone

class DoctorRegistrationForm(forms.ModelForm):
    class Meta:
        model = DoctorRequests
        fields = ['degree', 'specialization', 'address', 'experience', 'photo']