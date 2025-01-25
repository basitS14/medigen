from django.shortcuts import render, redirect , get_object_or_404
from django.http import HttpResponse
from django.urls import reverse
from django.contrib import messages
from django.utils import timezone
from datetime import datetime, timedelta, time

from .models import Doctors, CustomUser , Availability , Appointment
from .forms import UserRegistrationForm , DoctorRegistrationForm

from django.contrib.auth import   authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from datetime import datetime, time
from django.contrib.auth.decorators import login_required

from django.http import JsonResponse

# from helper import  generate_time_slots  , get_time_slots



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
                    auth_login(request=request , user=user)
                    return redirect(reverse("home"))
                else:
                    user.delete()  # Delete the user if doctor form is invalid
                    return render(request, 'index.html', {'user_form': user_form, 'doctor_form': doctor_form})
            else:
                auth_login(request=request , user=user)

            messages.success(request, 'Registration successful. Please log in.')
            return redirect(reverse('meds:login'))
        else:
            if role == '2':
                doctor_form = DoctorRegistrationForm(request.POST, request.FILES)
                return render(request, 'signup.html', {'user_form': user_form, 'doctor_form': doctor_form})
            return render(request, 'signup.html', {'user_form': user_form})
    
    return render(request, 'index.html')

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
        return redirect(reverse('meds:profile'))

            
    return render(request , 'available.html')


def login(request):
    if request.method == 'POST':
        email = request.POST.get('loginEmail')
        password = request.POST.get('loginPassword')

        user = authenticate(request, username=email, password=password)

        if user is not None:
            auth_login(request, user)
            messages.success(request, "Successfully logged in.")
            return redirect(reverse('meds:profile'))  # Make sure 'home' is defined in your urls.py
        else:
            messages.error(request, "Invalid email or password.")

    return render(request, 'index.html')

def profile(request):
    user = request.user
    doctor = None
    availability = None
    appointments = None
    
    if hasattr(user, 'doctors'):
        # Doctor profile
        doctor = user.doctors
        availability = doctor.availabilities.all()
        appointments = doctor.doctor_appointments.all().order_by('date', 'start_time')
        
        context = {
            'user': user,
            'doctor': doctor,
            'availability': availability,
            'appointments': appointments
        }
        return render(request, 'profile.html', context)
    else:
        # Patient profile
        appointments = user.patient_appointments.all().order_by('date', 'start_time')
        context = {
            'user': user,
            'appointments': appointments
        }
        return render(request, 'p_profile.html', context)

def p_profile(request):
    user = request.user
    appointments = user.patient_appointments.all().order_by('date', 'start_time')
    
    context = {
        'user': user,
        'appointments': appointments
    }
    return render(request, 'p_profile.html', context)

def logout(request):
    auth_logout(request)
    messages.success(request, "Successfully logged out.")
    return redirect('home')  # Redirect to home page after logout

def generate_time_slots(start_time, end_time, duration=15):
    """Generate time slots between start_time and end_time with given duration in minutes"""
    slots = []
    current = start_time
    while current < end_time:
        slot_end = (datetime.combine(datetime.today(), current) + timedelta(minutes=duration)).time()
        if slot_end <= end_time:
            slots.append({
                'start': current,
                'end': slot_end
            })
        current = slot_end
    return slots

def get_available_slots(doctor, selected_date):
    """Get available slots for a doctor on a specific date"""
    # Get day of week for selected date
    day_of_week = selected_date.strftime('%A')
    
    # Get doctor's availability for this day
    availability = doctor.availabilities.filter(day_of_week=day_of_week).first()
    
    if not availability:
        return []
    
    # Generate all possible time slots
    all_slots = generate_time_slots(availability.available_from, availability.available_to)
    
    # Get existing appointments for this doctor and date
    existing_appointments = Appointment.objects.filter(
        doctor=doctor,
        date=selected_date
    ).values_list('start_time', flat=True)
    
    # Current time
    current_time = timezone.localtime().time()
    current_date = timezone.localtime().date()
    
    # Filter available slots
    available_slots = []
    for slot in all_slots:
        # Skip if slot is in the past
        if selected_date == current_date and slot['start'] <= current_time:
            continue
        
        # Check if slot is already booked
        if slot['start'] not in existing_appointments:
            available_slots.append({
                'start_time': slot['start'],
                'end_time': slot['end'],
                'formatted_time': f"{slot['start'].strftime('%I:%M %p')} - {slot['end'].strftime('%I:%M %p')}"
            })
    
    return available_slots

def book_appointment(request, doctor_id):
    doctor = get_object_or_404(Doctors, id=doctor_id)
    current_date = timezone.localtime().date()
    
    # Get selected date from query params or use current date
    selected_date_str = request.GET.get('date', current_date.strftime('%Y-%m-%d'))
    selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
    
    # Handle AJAX request for time slots
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        available_slots = get_available_slots(doctor, selected_date)
        return JsonResponse({
            'slots': [
                {
                    'start_time': slot['start_time'].strftime('%H:%M'),
                    'formatted_time': slot['formatted_time']
                } for slot in available_slots
            ]
        })
    
    if request.method == 'POST':
        date_str = request.POST.get('date')
        slot_start_str = request.POST.get('slot_start')
        notes = request.POST.get('notes', '')
        
        # Convert strings to date and time objects
        appointment_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        slot_start = datetime.strptime(slot_start_str, '%H:%M').time()
        slot_end = (datetime.combine(appointment_date, slot_start) + timedelta(minutes=15)).time()
        
        # Check if slot is still available
        existing_appointment = Appointment.objects.filter(
            doctor=doctor,
            date=appointment_date,
            start_time=slot_start
        ).exists()
        
        if existing_appointment:
            messages.error(request, 'Sorry, this slot has already been booked. Please select another slot.')
            return redirect('meds:book_appointment', doctor_id=doctor_id)
        
        # Create appointment
        appointment = Appointment.objects.create(
            doctor=doctor,
            patient=request.user,
            date=appointment_date,
            start_time=slot_start,
            end_time=slot_end,
            notes=notes
        )
        
        messages.success(request, 'Appointment booked successfully!')
        return redirect('meds:profile')
    
    # Get available slots for selected date
    # Initial page load
    available_slots = get_available_slots(doctor, selected_date)
    context = {
        'doctor': doctor,
        'available_slots': available_slots,
        'selected_date': selected_date,
        'min_date': current_date,
    }
    
    return render(request, 'appointment.html', context)

def get_doctor_availability(request, doctor_id):
    doctor = get_object_or_404(Doctors, id=doctor_id)
    date_str = request.GET.get('date')
    
    if not date_str:
        return JsonResponse({'error': 'Date is required'}, status=400)
    
    try:
        selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        available_slots = get_available_slots(doctor, selected_date)
        
        return JsonResponse({
            'slots': [
                {
                    'start_time': slot['start_time'].strftime('%H:%M'),
                    'formatted_time': slot['formatted_time']
                } for slot in available_slots
            ]
        })
    except ValueError:
        return JsonResponse({'error': 'Invalid date format'}, status=400)




def test(request):
    return render(request , 'update_profile.html')



