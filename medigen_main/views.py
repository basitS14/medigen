from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from django.http import HttpResponse
from meds.models import Doctors , Availability, Prescription, Medicine
from datetime import datetime, time

def home(request):
    doctors = Doctors.objects.all()
    availability = Availability.objects.all()
    

    context = {
        'doctors' : doctors,
        'availability':availability
    }

    return render(request , 'index.html' , context=context)

def doc_profile(request , doctor_id):
    doctor = get_object_or_404(Doctors , id = doctor_id)
    availability = doctor.availabilities.all()
    online_fulltime = doctor.online_availabilities_fulltime.all()
    online_partime = doctor.online_availabilities_partime.all()

    context = {
        'doctor': doctor,
        'availability': availability,
        'online_fulltime': online_fulltime,
        'online_partime': online_partime
    }
    return render(request , 'doctor-profile.html' , context)



def test(request):
    return render(request , 'update_profile.html')



def know_more(request):
    doctors = Doctors.objects.all()
    availability = Availability.objects.all()
    
    context = {
        'doctors': doctors,
        'availability': availability
    }
    return render(request, 'know_more.html', context=context)

def learn_more(request):
   
    return render(request , 'learn.more.html' )

def expert_doctors(request):
    doctors = Doctors.objects.all()
    availability = Availability.objects.all()
    

    context = {
        'doctors' : doctors,
        'availability':availability
    }
    return render(request , 'EDL.html' , context=context)

def online_consultation(request):
    return render(request , 'online-consultation.html')

def check_disease(request):
    return render(request , 'check-your-disease.html')

def sign_up(request):
    return render(request , "login_modal.html")

def add_prescription(request):
    if request.method == 'POST':
        patient_name = request.POST.get('patient_name')
        patient_age = request.POST.get('patient_age')
        patient_gender = request.POST.get('patient_gender')
        diagnosis = request.POST.get('diagnosis')
        medicine_count = int(request.POST.get('medicine_count', 0))
        
        # Create prescription
        prescription = Prescription.objects.create(
            patient_name=patient_name,
            patient_age=patient_age,
            patient_gender=patient_gender,
            diagnosis=diagnosis,
            doctor=request.user.doctor,
            date=timezone.now()
        )
        
        # Add medicines
        for i in range(medicine_count):
            name = request.POST.get(f'medicine_name_{i}')
            dosage = request.POST.get(f'medicine_dosage_{i}')
            timings = request.POST.getlist(f'medicine_timing_{i}')  # Get all selected timings
            quantity = request.POST.get(f'medicine_quantity_{i}')
            duration = request.POST.get(f'medicine_duration_{i}')
            instructions = request.POST.get(f'medicine_instructions_{i}')
            
            if name and dosage and timings:  # Ensure required fields are present
                Medicine.objects.create(
                    prescription=prescription,
                    name=name,
                    dosage=dosage,
                    timing=', '.join(timings),  # Join multiple timings with commas
                    quantity=quantity,
                    duration=duration,
                    special_instructions=instructions
                )
        
        return redirect('view_prescription', prescription_id=prescription.id)
    
    return render(request, 'add_prescription.html')
