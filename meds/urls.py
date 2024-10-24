from django.contrib import admin
from django.urls import path , include
from . import views

app_name = "meds"
urlpatterns = [
    path("" , views.meds , name = "meds"),
    path("register/" , views.register , name="register"),
    path("available/" , views.doc_availability , name = "available"),
    path("login/" , views.login , name = "login"),
    path("profile/" , views.profile , name = "profile"),
    path('logout/', views.logout, name='logout'),
    path('p_profile' , views.p_profile , name = 'p_profile'),
    path('book-appointment/<int:doctor_id>/', views.book_appointment, name='book_appointment'),
    path('doctor/<int:doctor_id>/availability/', views.get_doctor_availability, name='get_doctor_availability'),


    path('__reload__' , include('django_browser_reload.urls')),

]
