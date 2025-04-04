from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from django.http import HttpResponse
from meds.models import Doctors , Availability 
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

    context = {
        'doctor':doctor,
        'availability':availability
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
