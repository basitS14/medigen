from datetime import datetime, timedelta
from django.db.models import Count
from django.utils import timezone


from datetime import datetime, timedelta, time

def get_time_slots(doctor_id, date_str):
    # Retrieve the doctor and availability
    doctor = get_object_or_404(Doctors, id=doctor_id)
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    day = date_obj.strftime("%A")

    # Filter availability for the given day
    availability = doctor.availabilities.filter(day_of_week=day).first()
    if not availability:
        return []  # Return empty if no availability found for the given day

    # Get start and end time from TimeField
    start_time = availability.available_from
    end_time = availability.available_to

    # Convert TimeField to datetime for manipulation
    current = datetime.combine(date_obj, start_time)
    end = datetime.combine(date_obj, end_time)

    slots = []

    # Generate 10-minute slots
    while current.time() < end.time():
        slot_start = current.strftime("%H:%M")
        current += timedelta(minutes=10)
        slot_end = current.strftime("%H:%M")
        slots.append((slot_start, slot_end))

    return slots



        
    




# def get_time_slots(doctor_id, date_str):
#     """
#     Get available time slots for a doctor on a specific date.
#     Each slot is one hour long and can accommodate max_appointments patients.
    
#     Args:
#         doctor_id: The ID of the doctor
#         date_str: Date string in YYYY-MM-DD format
#     """
#     try:
#         # Convert date string to datetime object
#         date = datetime.strptime(date_str, '%Y-%m-%d').date() if isinstance(date_str, str) else date_str
        
#         # Get day of week for the selected date
#         day_of_week = date.strftime('%A')
        
#         # Fetch doctor's availability for the given day of week
#         availability = Availability.objects.filter(
#             doctor_id=doctor_id,
#             day_of_week=day_of_week
#         ).first()
        
#         if not availability:
#             return []
        
#         # Generate hourly time slots
#         slots = generate_time_slots(
#             availability.available_from,
#             availability.available_to
#         )
        
#         # Get booked appointments for each hour slot
#         booked_appointments = Appointment.objects.filter(
#             doctor_id=doctor_id,
#             date=date
#         ).values('start_time').annotate(count=Count('id'))
        
#         # Create a dictionary of booked slots with counts
#         booked_slots = {
#             appointment['start_time'].strftime('%H:00'): appointment['count'] 
#             for appointment in booked_appointments
#         }
        
#         # Prepare slot data with booking status
#         slot_data = []
#         current_datetime = timezone.localtime()
        
#         for start_time, end_time in slots:
#             # Create datetime objects for comparison
#             slot_datetime = datetime.combine(date, start_time)
            
#             # Skip slots that are in the past
#             if date == current_datetime.date() and slot_datetime <= current_datetime:
#                 continue
                
#             # Get number of bookings for this slot
#             slot_key = start_time.strftime('%H:00')
#             bookings_count = booked_slots.get(slot_key, 0)
            
#             # Check if slot is fully booked
#             is_fully_booked = bookings_count >= availability.max_appointments
            
#             slot_data.append({
#                 'start_time': start_time,
#                 'end_time': end_time,
#                 'is_fully_booked': is_fully_booked,
#                 'available_spots': availability.max_appointments - bookings_count,
#                 'total_spots': availability.max_appointments
#             })
        
#         return slot_data
        
#     except Exception as e:
#         print(f"Error in get_time_slots: {str(e)}")
#         return []

# def generate_time_slots(available_from, available_to):
#     """
#     Generate hourly time slots between available_from and available_to times.
    
#     Args:
#         available_from: Start time of availability
#         available_to: End time of availability
#     """
#     try:
#         slots = []
#         current_time = datetime.combine(datetime.today(), available_from)
#         end_time = datetime.combine(datetime.today(), available_to)
        
#         # Generate hourly slots
#         while current_time < end_time:
#             next_time = current_time + timedelta(hours=1)
#             # Only add the slot if it creates a full hour
#             if next_time <= end_time:
#                 slots.append((current_time.time(), next_time.time()))
#             current_time = next_time
        
#         return slots
        
#     except Exception as e:
#         print(f"Error in generate_time_slots: {str(e)}")
#         return []