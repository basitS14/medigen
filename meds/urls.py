from django.contrib import admin
from django.urls import path , include
from . import views

app_name = "meds"
urlpatterns = [
    path("" , views.meds , name = "meds"),
    path("register/" , views.register , name="register"),
    path("available/" , views.doc_availability_offline , name = "available"),
    path("online_available_fulltime/", views.doc_availability_online_fulltime , name="online_available_fulltime"),
    path("online_available_partime/", views.doc_availability_online_partime , name="online_available_partime"),
    path("login/" , views.login , name = "login"),
    path("profile/" , views.profile , name = "profile"),
    path('logout/', views.logout, name='logout'),
    path('p_profile' , views.p_profile , name = 'p_profile'),
    path('test/' , views.test , name="test"),
    path('book-appointment/<int:doctor_id>/', views.book_appointment, name='book_appointment'),
    path("get-time-slots/<int:doctor_id>/", views.get_time_slots, name="get_time_slots"),
    path('video-call/<int:appointment_id>/', views.video_call, name='video-call'),
    path('approve-doctor/<int:doctor_id>/', views.approve_doctor, name='approve_doctor'),
    path('reject-doctor/<int:doctor_id>/', views.reject_doctor, name='reject_doctor'),
    path('request_document_verification/<int:doctor_id>/' , views.request_document_verification , name="request_document_verification"),
    path('verify-otp/<int:user_id>', views.verify_otp, name='verify_otp'),
    path('resend-otp/', views.resend_otp, name='resend_otp'),
    path('update-profile/',views.update_profile , name='update_profile'),
    path('update-doctor-profile/', views.update_doctor_profile, name='update_doctor_profile'),
    path('change_email/',views.change_email , name="change_email"),
    path('verify-email-change/', views.verify_email_change, name='verify_email_change'),
    path('resend-email-change-otp/', views.resend_email_change_otp, name='resend_email_change_otp'),
    path('bmi-calculator/' , views.caluculate_bmi , name='bmi-calculator'),
    path('add-prescription/<int:appointment_id>/', views.add_prescription, name='add_prescription'),
    path('view-prescription/<int:appointment_id>/', views.view_prescription, name='view_prescription'),
    path('__reload__' , include('django_browser_reload.urls')),

]
