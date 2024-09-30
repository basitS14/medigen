from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse
from django.contrib import messages
from .models import Doctors, CustomUser

def meds(request):
    return HttpResponse("You are on home page")

def register(request):
    if request.method == 'POST':
        full_name = request.POST.get('fullName')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        gender = request.POST.get('gender')
        dob = request.POST.get('dob')
        password = request.POST.get('password')
        role = request.POST.get('role')

        try:
            user = CustomUser.objects.create_user(
                full_name=full_name,
                email=email,
                password=password,
                phone=phone,
                gender=gender,
                dob=dob,
            )

            if role == '2':  # Doctor
                degree = request.POST.get('degree')
                specialization = request.POST.get('specialization')
                address = request.POST.get('address')
                image_upload = request.FILES.get('image_upload')  # Note the change to request.FILES

                Doctors.objects.create(
                    user=user,
                    degree=degree,
                    specialization=specialization,
                    address=address,
                    photo=image_upload,
                )

            messages.success(request, 'Registration successful. Please log in.')
            return redirect(reverse('meds:login'))  # Use reverse() to get the URL

        except Exception as e:
            messages.error(request, f'Registration failed: {str(e)}')
            return redirect(reverse('meds:register'))

    return render(request, 'signup.html')

def login(request):
    return render(request, 'LogIn.html')

def profile(request):
    return render(request, 'update_profile.html')