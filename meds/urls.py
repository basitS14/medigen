from django.contrib import admin
from django.urls import path , include
from . import views

app_name = "meds"
urlpatterns = [
    path("" , views.meds , name = "meds"),
    path("register/" , views.register , name="register"),
    path("login/" , views.login , name = "login"),
    path("profile/" , views.profile , name = "profile"),
    path('logout/', views.logout, name='logout'),
    # path("disease_prediction/" ,views.multidisease , name = 'disease_prediction' ),                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       
    path("test/" , views.test , name = 'test'),
    path('__reload__' , include('django_browser_reload.urls')),

]
