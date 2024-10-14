from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse
from django.contrib import messages
from .models import Doctors, CustomUser , Availability
from .forms import UserRegistrationForm , DoctorRegistrationForm

from django.contrib.auth import   authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout



def meds(request):
    return HttpResponse("You are on home page")

def register(request):
    if request.method == 'POST':
        user_data = {
            "full_name": request.POST.get('fullName'),
            "email": request.POST.get('email'),
            "phone": request.POST.get('phone'),
            "gender": request.POST.get('gender'),
            "dob": request.POST.get('dob'),
            "password": request.POST.get('password'),
        }
        role = request.POST.get('role')
        
        user_form = UserRegistrationForm(user_data)
        if user_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_data['password'])
            user.save()
            
            if role == '2':  # Doctor
                doctor_form = DoctorRegistrationForm(request.POST, request.FILES)
                # days = request.POST.getlist('days')
                if doctor_form.is_valid():
                    doctor = doctor_form.save(commit=False)
                    doctor.user = user
                    doctor.save()
                    return redirect(reverse("meds:login"))
                else:
                    user.delete()  # Delete the user if doctor form is invalid
                    return render(request, 'signup.html', {'user_form': user_form, 'doctor_form': doctor_form})

            messages.success(request, 'Registration successful. Please log in.')
            return redirect(reverse('meds:login'))
        else:
            if role == '2':
                doctor_form = DoctorRegistrationForm(request.POST, request.FILES)
                return render(request, 'signup.html', {'user_form': user_form, 'doctor_form': doctor_form})
            return render(request, 'signup.html', {'user_form': user_form})
    
    return render(request, 'signup.html')

def doc_availability(request):
    if request.method == 'POST':
        days = request.POST.getlist('days')

        for day in days:
            available_from = request.POST.get(f'{day.lower()}_from')
            available_to = request.POST.get(f'{day.lower()}_to')

            availability = Availability(
                doctor=request.user.doctors,
                day_of_week=day,
                available_from=available_from,
                available_to=available_to
            )
            availability.save()
        messages.success(request, 'Registration successful. Please log in.')
        return redirect(reverse('meds:login'))

            
    return render(request , 'available.html')


def login(request):
    if request.method == 'POST':
        email = request.POST.get('loginEmail')
        password = request.POST.get('loginPassword')

        user = authenticate(request, username=email, password=password)
        
        # user_list = CustomUser.objects.values_list('email')
        
        # print(user)
        

        # if user in doctors_list:
        #     doctor = Doctors.objects.filter(user=user).values()

        if user is not None:
            auth_login(request, user)
            messages.success(request, "Successfully logged in.")
            return redirect(reverse('meds:profile'))  # Make sure 'home' is defined in your urls.py
        else:
            messages.error(request, "Invalid email or password.")

    return render(request, 'LogIn.html')

# @login_required
def profile(request):
    user  = request.user
    doctor = None
    availablity = None
    # doctor = request.doctor
    if hasattr(user , 'doctors'):
        doctor = user.doctors
        availability = doctor.availabilities.all()


    context = {
        'user': user,
        'doctor':doctor,
        'availability':availability
        # 'asmer' : 'ajh'
        
    }
    return render(request,'profile.html' , context)

def logout(request):
    auth_logout(request)
    messages.success(request, "Successfully logged out.")
    return redirect('home')  # Redirect to home page after logout



def test(request):
    return render(request , 'update_profile.html')

