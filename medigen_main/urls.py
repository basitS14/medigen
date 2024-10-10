
from django.contrib import admin
from django.urls import path , include
from . import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("" , views.home, name = "home" ),
    path("know_more/" ,views.know_more , name= "know_more" ),
    path("meds/" , include("meds.urls")),
    path("models/" , include("models.urls")),
    path('__reload__' , include('django_browser_reload.urls'))

    

]
