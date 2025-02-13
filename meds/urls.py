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



    path('__reload__' , include('django_browser_reload.urls')),

]
