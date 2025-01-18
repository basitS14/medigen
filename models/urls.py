from django.contrib import admin
from django.urls import path , include
from . import views

app_name = "models"
urlpatterns = [
    
path('' , views.model , name = "models"),
path('multi_disease/' , views.multidisease , name  = "multi_disease"),
path('__reload__' , include('django_browser_reload.urls')),
path('results' , views.results , name = "results"),
path("skin_disease/" , views.skin_disease , name="skin_disease")

]
