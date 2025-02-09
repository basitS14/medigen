from django.shortcuts import render, redirect , get_object_or_404
from django.http import HttpResponse
from django.urls import reverse
from django.contrib import messages
from django.utils import timezone

from .models import Doctors, CustomUser , Availability , Appointment , OnlineAvailability , OnlineAvailabilityPartime
from .forms import UserRegistrationForm , DoctorRegistrationForm

from django.contrib.auth import   authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from datetime import datetime, time
from django.contrib.auth.decorators import login_required

from django.http import JsonResponse

from datetime import datetime, timedelta, time
import json


# Helper Functions 

def generate_time_slots(start_time, end_time, break_start, break_end, max_patients):
    """Generate time slots between start_time and end_time"""
    fmt = "%H:%M"
    start_time = datetime.strptime(start_time.strftime(fmt), fmt)
    end_time = datetime.strptime(end_time.strftime(fmt), fmt)
    break_start = datetime.strptime(break_start.strftime(fmt), fmt)
    break_end = datetime.strptime(break_end.strftime(fmt), fmt)

    duration = timedelta(minutes=(60//max_patients))    
    slots = []
    current = start_time
    
    while current + duration <= end_time:
        slot_end = current + duration
        if not(break_start <= current < break_end or break_start < slot_end <= break_end):
            slots.append({
                'start': current.time(),
                'end': slot_end.time()
            })
        current = slot_end
    return slots

def generate_time_slots_partime(start_time, end_time, max_patients):
    """Generate time slots between start_time and end_time"""
    fmt = "%H:%M"
    start_time = datetime.strptime(start_time.strftime(fmt), fmt)
    end_time = datetime.strptime(end_time.strftime(fmt), fmt)


    duration = timedelta(minutes=(60//max_patients))    
    slots = []
    current = start_time
    
    while current + duration <= end_time:
        slot_end = current + duration
   
        slots.append({
            'start': current.time(),
            'end': slot_end.time()
        })
        current = slot_end
    return slots

def check_doctor_availabilty(doctor_id):
    offline_slots = {}
    online_slots = {}

    doctor = Doctors.objects.filter(id=int(doctor_id)).first()
    available = Availability.objects.filter(doctor=doctor)
    online_available = OnlineAvailability.objects.filter(doctor=doctor)
    online_available_partime = OnlineAvailabilityPartime.objects.filter(doctor=doctor)

    if available:
         for s in available.all():
            offline_slots[s.day_of_week] = generate_time_slots(
            start_time=s.available_from,
            end_time=s.available_to,
            break_start=s.break_from,
            break_end=s.break_to,
            max_patients = s.max_appointments
        )

    if online_available:
        for s in online_available.all():
            online_slots[s.day_of_week] = generate_time_slots(
                start_time=s.available_from,
                end_time=s.available_to,
                break_start=s.break_from,
                break_end=s.break_to,
                max_patients = s.max_appointments

            )

    if online_available_partime:
        for s in online_available_partime.all():
            online_slots[s.day_of_week] = generate_time_slots_partime(
                start_time=s.available_from,
                end_time=s.available_to,
                max_patients = s.max_appointments

            )
    return offline_slots, online_slots

# Views start from here

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
                if doctor_form.is_valid():
                    doctor = doctor_form.save(commit=False)
                    doctor.user = user
                    doctor.save()
                    auth_login(request=request, user=user)
                    return redirect(reverse("home"))
                else:
                    user.delete()
                    return render(request, 'index.html', {
                        'user_form': user_form, 
                        'doctor_form': doctor_form,
                        'form_errors': doctor_form.errors
                    })
            else:
                auth_login(request=request, user=user)
                return redirect(reverse('meds:profile'))

        else:
            return render(request, 'index.html', {
                'user_form': user_form,
                'form_errors': user_form.errors
            })
    
    return render(request, 'index.html')

def doc_availability_offline(request):
    if request.method == 'POST':
        days = request.POST.getlist('days')

        for day in days:
            available_from = request.POST.get(f'available_from_{day.lower()}')
            available_to = request.POST.get(f'available_to_{day.lower()}')
            break_from = request.POST.get(f'break_from_{day.lower()}')
            break_to = request.POST.get(f'break_to_{day.lower()}')
            max_appointments = request.POST.get('patientCapacity')

            availability = Availability(
                doctor=request.user.doctors,
                day_of_week=day,
                available_from=available_from,
                available_to=available_to,
                break_from = break_from,
                break_to = break_to,
                max_appointments = max_appointments

            )
            availability.save()
        messages.success(request, 'Registration successful. Please log in.')
        return redirect(reverse('meds:profile'))

            
    return render(request , 'availability.html')


def doc_availability_online_fulltime(request):
    if request.method == 'POST':
        days = request.POST.getlist('online_days')
        max_appointments = request.POST.get('patientCapacity')

        for day in days:
            available_from = request.POST.get(f'available_from_{day.lower()}')
            available_to = request.POST.get(f'available_to_{day.lower()}')
            break_from = request.POST.get(f'break_from_{day.lower()}')
            break_to = request.POST.get(f'break_to_{day.lower()}')

            availability = OnlineAvailability(
                doctor=request.user.doctors,
                day_of_week=day,
                available_from=available_from,
                available_to=available_to,
                break_from = break_from,
                break_to = break_to,
                max_appointments = max_appointments

            )
            availability.save()
        messages.success(request, 'Registration successful. Please log in.')
        return redirect(reverse('meds:profile'))
            
    return render(request , 'availability.html')

def doc_availability_online_partime(request):
    if request.method == 'POST':
        days = request.POST.getlist('online_days_partime')

        for day in days:
            available_from = request.POST.get(f'available_from_{day.lower()}')
            available_to = request.POST.get(f'available_to_{day.lower()}')
            max_appointments = request.POST.get('patientCapacity')

            availability = OnlineAvailabilityPartime(
                doctor=request.user.doctors,
                day_of_week=day,
                available_from=available_from,
                available_to=available_to,
                max_appointments = max_appointments

            )
            availability.save()
        messages.success(request, 'Registration successful. Please log in.')
        return redirect(reverse('meds:profile'))
            
    return render(request , 'availability.html')

        


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



# In views.py, modify the get_time_slots view:

from django.db.models import Q

def get_time_slots(request, doctor_id):
    selected_date = request.GET.get("date")
    mode = request.GET.get("mode")

    if not all([selected_date, mode]):
        return JsonResponse({"error": "Missing parameters"}, status=400)

    try:
        # Get day of the week
        day_of_week = datetime.strptime(selected_date, "%Y-%m-%d").strftime("%A")

        doctor = get_object_or_404(Doctors, id=doctor_id)
        
        slots = []
        if mode == "offline":
            availability = Availability.objects.filter(doctor=doctor, day_of_week=day_of_week).first()
            if availability:
                slots = generate_time_slots(
                    start_time=availability.available_from,
                    end_time=availability.available_to,
                    break_start=availability.break_from,
                    break_end=availability.break_to,
                    max_patients=availability.max_appointments
                )
        elif mode == "online":
            online_availability = OnlineAvailability.objects.filter(doctor=doctor, day_of_week=day_of_week).first()
            online_partime = OnlineAvailabilityPartime.objects.filter(doctor=doctor, day_of_week=day_of_week).first()

            if online_availability:
                slots = generate_time_slots(
                    start_time=online_availability.available_from,
                    end_time=online_availability.available_to,
                    break_start=online_availability.break_from,
                    break_end=online_availability.break_to,
                    max_patients=online_availability.max_appointments
                )
            elif online_partime:
                slots = generate_time_slots_partime(
                    start_time=online_partime.available_from,
                    end_time=online_partime.available_to,
                    max_patients=online_partime.max_appointments
                )

        # **Filter Out Already Booked Slots**
        booked_slots = Appointment.objects.filter(
            doctor=doctor,
            date=selected_date
        ).values_list('start_time', 'end_time')

        # Convert booked slots to a set of tuples for quick lookup
        booked_slots_set = {(slot[0].strftime('%H:%M'), slot[1].strftime('%H:%M')) for slot in booked_slots}

        # Remove booked slots from available slots
        available_slots = []
        for slot in slots:
            slot_start = slot['start'].strftime('%H:%M')
            slot_end = slot['end'].strftime('%H:%M')
            if (slot_start, slot_end) not in booked_slots_set:
                available_slots.append({'start': slot_start, 'end': slot_end})

        return JsonResponse({"slots": available_slots})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

def book_appointment(request, doctor_id):
    if request.method == "POST":
        patient_name = request.POST.get('patient-name')
        date = request.POST.get('date')
        selected_slot = request.POST.get('selected_slot')
        notes = request.POST.get('notes')

        doctor = get_object_or_404(Doctors, id=doctor_id)
        username = request.user
        # Handle slot selection (split start and end time)
        if selected_slot:
            slot_start, slot_end = selected_slot.split('-')
            
            # You can convert this into a datetime or handle as needed
            # Here we'll just store the start and end time for simplicity
            appointment = Appointment.objects.create(
                doctor=doctor,
                patient=patient_name,
                date=date,
                start_time=slot_start,
                end_time=slot_end,
                notes=notes,
                username=username
            )
        
        return redirect('meds:p_profile') # Redirect to appointment listing page after booking
    else:
        # You can pass additional context like doctor details if needed
        return render(request, 'index.html' )

    return render(request, 'index.html')

def test(request):
    return render(request , 'book_appointment.html')



