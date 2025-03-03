from django.contrib import admin
from .models import Doctors, CustomUser , Availability , Appointment , OnlineAvailability , OnlineAvailabilityPartime , DoctorRequests , VerificationData , BMI

admin.site.register(Doctors)
admin.site.register(CustomUser)
admin.site.register(Availability)
admin.site.register(Appointment)
admin.site.register(OnlineAvailability)
admin.site.register(OnlineAvailabilityPartime)
admin.site.register(DoctorRequests)
admin.site.register(VerificationData)
admin.site.register(BMI)



