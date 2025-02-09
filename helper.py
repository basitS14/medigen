from datetime import datetime, timedelta
from django.db.models import Count
from django.utils import timezone
from meds.models import Doctors, CustomUser , Availability , Appointment , OnlineAvailability , OnlineAvailabilityPartime

from datetime import datetime, timedelta, time

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
    doctor = Doctors.objects.filter(id=int(doctor_id)).first()
    available = Availability.objects.filter(doctor=doctor)
    print(available)






