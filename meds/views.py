from django.shortcuts import render, redirect , get_object_or_404
from django.http import HttpResponse
from django.urls import reverse
from django.contrib import messages
from django.utils import timezone

from .models import Doctors, CustomUser , Availability , Appointment , OnlineAvailability , OnlineAvailabilityPartime , DoctorRequests , VerificationData
from .forms import UserRegistrationForm , DoctorRegistrationForm
from django import forms

from django.contrib.auth import   authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from datetime import datetime, time
from django.contrib.auth.decorators import login_required

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

import os
from dotenv import load_dotenv

from django.http import JsonResponse

from datetime import datetime, timedelta, time
import json

import time
from agora_token_builder import RtcTokenBuilder
import random
from django.core.mail import send_mail
import pyotp

load_dotenv()

# Helper Functions 

def handle_uploaded_file(f):
    # Helper function to handle file upload
    from django.core.files.storage import default_storage
    import os
    
    file_name = f'temp/{f.name}'
    with default_storage.open(file_name, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    return file_name

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

def generate_otp(email):
    otp = pyotp.TOTP(pyotp.random_base32(), interval=300).now()
    verification_data, created = VerificationData.objects.get_or_create(email=email)
    verification_data.email_otp = otp
    verification_data.save()
    return otp

# def verify_otp(otp, user_otp):
#     return otp == user_otp



# Views start from here

def meds(request):
    return HttpResponse("You are on home page")


from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth import login as auth_login
from django.utils import timezone
from datetime import timedelta

def register(request):
    if request.method == 'POST':
        user_data = {
            "full_name": request.POST.get('full_name'),  
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
            user.is_active = False  # Set user as inactive until email is verified
            user.save()
            
            # Generate and store OTP
            otp = generate_otp(user.email)
            request.session['otp'] = otp
            request.session['user_id'] = user.id
            # Store current time as timestamp
            request.session['registration_timestamp'] = timezone.now().timestamp()
            
            if role == '2':  # Doctor
                doctor_form = DoctorRegistrationForm(request.POST, request.FILES)
                if doctor_form.is_valid():
                    request.session['doctor_data'] = {
                        'degree': request.POST.get('degree'),
                        'specialization': request.POST.get('specialization'),
                        'address': request.POST.get('address'),
                        'experience': request.POST.get('experience'),
                    }
                    if 'photo' in request.FILES:
                        request.session['has_photo'] = True
                        request.session['photo_name'] = request.FILES['photo'].name
                    
                    request.session['is_doctor'] = True
                else:
                    user.delete()
                    return render(request, 'index.html', {
                        'user_form': user_form,
                        'doctor_form': doctor_form,
                        'form_errors': doctor_form.errors
                    })
            else:
                request.session['is_doctor'] = False
            
            # # Send OTP email
            # generate_otp(user.email)
            
            send_mail(
                "Email Verification OTP",
                f"Your OTP for MediGen registration is: {otp}",
                os.getenv("GMAIL_ADDRESS"),
                [user.email],
                fail_silently=False,
            )
            print("Mail Sent")
            
            return redirect(reverse('meds:verify_otp', kwargs={'user_id': user.id}))
        else:
            return render(request, 'index.html', {
                'user_form': user_form,
                'form_errors': user_form.errors
            })
    
    return render(request, 'index.html')

def verify_otp(request, user_id):
    # Check if verification window has expired (30 minutes)
    registration_timestamp = request.session.get('registration_timestamp')
    if registration_timestamp:
        # Convert timestamp to timezone-aware datetime
        registration_datetime = timezone.datetime.fromtimestamp(
            registration_timestamp, 
            tz=timezone.get_current_timezone()
        )
        elapsed_time = timezone.now() - registration_datetime
        
        if elapsed_time > timedelta(minutes=30):
            # Delete unverified user and clean up
            try:
                user = CustomUser.objects.get(id=user_id)
                user.delete()
            except CustomUser.DoesNotExist:
                pass
            print("Verification window expired. Please register again.")
            messages.error(request, "Verification window expired. Please register again.")
            return redirect('meds:register')

    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        stored_otp = request.session.get('otp')

        print("inside request")
        if entered_otp == stored_otp:
            try:
                print("saving user")
                user = CustomUser.objects.get(id=user_id)
                user.is_active = True
                user.email_verified = True
                user.save()
                print("user saved")

                is_doctor = request.session.get('is_doctor')
                if is_doctor:
                    doctor_data = request.session.get('doctor_data', {})
                    print("inside doctor verification")
                    # Create doctor request
                    doctor = DoctorRequests.objects.create(
                        user=user,
                        degree=doctor_data.get('degree'),
                        specialization=doctor_data.get('specialization'),
                        address=doctor_data.get('address'),
                        experience=doctor_data.get('experience'),
                        is_approved=False
                    )
                    
                    # Handle photo if it exists
                    if request.session.get('has_photo') and 'photo' in request.FILES:
                        doctor.photo = request.FILES['photo']
                        doctor.save()
                    print("doctor saved")
                    messages.success(request, "Doctor registration request submitted.")
                else:
                    messages.success(request, "Registration successful!")

                # Clean up session
                session_keys = ['user_id', 'otp', 'is_doctor', 'doctor_data', 
                              'has_photo', 'photo_name', 'registration_timestamp']
                for key in session_keys:
                    if key in request.session:
                        del request.session[key]
                print("deleted sessions keys")
                return redirect('meds:login')
            except CustomUser.DoesNotExist:
                messages.error(request, "User not found.")
                return redirect('meds:register')
        else:
            print("Invalid OTP")
            messages.error(request, "Invalid OTP.")

    return render(request, 'verification.html' , context={'user_id':user_id})

def resend_otp(request):
    if request.method == 'POST':
        user_id = request.session.get('user_id')
        if user_id:
            try:
                user = CustomUser.objects.get(id=user_id)
                
                # Check if within 30-minute window
                registration_timestamp = request.session.get('registration_timestamp')
                if registration_timestamp:
                    registration_datetime = timezone.datetime.fromtimestamp(
                        registration_timestamp,
                        tz=timezone.get_current_timezone()
                    )
                    elapsed_time = timezone.now() - registration_datetime
                    if elapsed_time > timedelta(minutes=30):
                        user.delete()
                        messages.error(request, "Verification window expired. Please register again.")
                        return redirect('meds:register')
                
                # Generate and send new OTP
                otp = generate_otp(user.email)
                request.session['otp'] = otp
                messages.success(request, "New OTP sent.")
                return redirect(reverse('meds:verify_otp', kwargs={'user_id': user_id}))
            except CustomUser.DoesNotExist:
                messages.error(request, "User not found.")
        else:
            messages.error(request, "Session expired, please register again.")
        
    return redirect('meds:register')


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




@login_required
def profile(request):
    user = request.user
    doctor = None
    availability = None
    appointments = None
    
    if user.is_superuser:
        pending_doctors = DoctorRequests.objects.filter(is_approved=False)
        doctors = Doctors.objects.all()

        context = {
            "pending_doctors":pending_doctors,
            "doctors":doctors
        }
        return render(request , "admin_panel.html" ,context = context )

    elif hasattr(user, 'doctors'):
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
        'appointments': appointments,
        'now':timezone.now(),
    }
    return render(request, 'p_profile.html', context)

def logout(request):
    auth_logout(request)
    messages.success(request, "Successfully logged out.")
    return redirect('home')  # Redirect to home page after logout


@login_required
def approve_doctor(request, doctor_id):
    if not request.user.is_superuser:
        messages.error(request, "Unauthorized action.")
        return redirect('meds:profile')

    doctor_request = DoctorRequests.objects.get(id=doctor_id)
    doctor_request.is_approved = True
    doctor_request.save()

    # Create a Doctors profile
    Doctors.objects.create(
        user=doctor_request.user,
        degree=doctor_request.degree,
        specialization=doctor_request.specialization,
        address=doctor_request.address,
        experience=doctor_request.experience,
        photo= doctor_request.photo
    )

    messages.success(request, f"Doctor {doctor_request.user.full_name} has been approved.")
    return redirect('meds:profile')


@login_required
def reject_doctor(request, doctor_id):
    if not request.user.is_superuser:
        messages.error(request, "Unauthorized action.")
        return redirect('meds:profile')

    doctor_request = DoctorRequests.objects.get(id=doctor_id)
    user = doctor_request.user
    doctor_request.delete()

    messages.warning(request, "Doctor request has been rejected.")
    return redirect('meds:profile')

def request_document_verification(request , doctor_id):
    docMail = DoctorRequests.objects.get(id=doctor_id).user.email



    send_mail(
    "Request for document verification",
    "Please verify your documents",
    os.getenv("GMAIL_ADDRESS"),
    [docMail],
    fail_silently=False,
    )

    return redirect("meds:profile" )


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
        mode = request.POST.get('mode')

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
                username=username,
                appointment_mode=mode,
                
            )
        
        return redirect('meds:p_profile') # Redirect to appointment listing page after booking
    else:
        # You can pass additional context like doctor details if needed
        return render(request, 'index.html' )

    return render(request, 'index.html')

@login_required
def video_call(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Check if user is either the doctor or patient
    if request.user != appointment.username and request.user != appointment.doctor.user:
        return HttpResponse("Unauthorized", status=403)
    
    # Check if appointment is for today
    today = timezone.now().date()
    if appointment.date != today:
        return HttpResponse("This appointment is not scheduled for today", status=403)

    # Agora credentials
    app_id = os.getenv('AGORA_APP_ID')
    app_certificate = os.getenv('AGORA_APP_CERTIFICATE')
    
    # Generate channel name based on appointment ID
    channel_name = f'appointment_{appointment.id}'
    
    # Get the other user
    other_user = appointment.doctor.user if request.user == appointment.username else appointment.username
    
    # Generate token
    expiration_time = 3600  # Token expires in 1 hour
    current_timestamp = int(time.time())
    privilege_expired_ts = current_timestamp + expiration_time
    
    token = RtcTokenBuilder.buildTokenWithUid(
        app_id, 
        app_certificate,
        channel_name,
        request.user.id,  # Use user ID as the UID
        1,  # Role: 1 for publisher/host
        privilege_expired_ts
    )
    
    context = {
        'appointment': appointment,
        'other_user': other_user,
        'agora_app_id': app_id,
        'token': token,
        'channel_name': channel_name,
    }
    
    return render(request, 'video_call.html', context)

def test(request):
    return render(request , 'book_appointment.html')



