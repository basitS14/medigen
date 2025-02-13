from django import forms
from django.core.exceptions import ValidationError
from .models import CustomUser , Doctors , DoctorRequests

class UserRegistrationForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['full_name' ,'email' , 'phone' , 'gender'  , 'dob' , 'password']
    def clean_email(self):
        email = self.cleaned_data.get("email")
        if CustomUser.objects.filter(email = email).exists():
            raise ValidationError("This email already exists")
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        if CustomUser.objects.filter(phone=phone).exists():
            raise ValidationError("This phone number already exists")
        return phone     

class DoctorRegistrationForm(forms.ModelForm):
    photo = forms.ImageField(
        required=True,
        error_messages={'required': "A profile photo is required for doctor registration."}
    )

    class Meta:
        model = DoctorRequests
        fields = ['degree', 'specialization', 'address', 'photo' , 'experience' , 'is_approved']

    def clean_photo(self):
        photo = self.cleaned_data.get('photo')
        if not photo:
            raise forms.ValidationError("A profile photo is required for doctor registration.")
        return photo