from django.contrib.auth.models import AbstractUser
from django.db import models
from .manager import CustomUserManager
import datetime as dt

GENDER = [
    ("Male" , "Male"),
    ("Female" , "Female"),
    ("Not Specified" , "Not Specified")
]

default_dob = dt.date(1999 , 8 , 16)

class CustomUser(AbstractUser):
    username = None
    first_name = None
    last_name =  None
    full_name = models.CharField(max_length=50)
    email = models.EmailField(unique = True)
    phone = models.CharField( max_length=15)
    gender = models.CharField(choices=GENDER , max_length=20 , default="Not Specified")
    dob = models.DateField( default=default_dob)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [ 'phone' , 'full_name']

    objects = CustomUserManager()

    def __str__(self):
        return self.email
    

class Doctors(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    degree = models.CharField( max_length=50)
    specialization = models.CharField(max_length=50)
    address = models.TextField()
    photo = models.ImageField( upload_to='static/photos' , default = "user-avatar.png")



    def __str__(self):
        return f"Dr.{self.user.full_name}"
    

