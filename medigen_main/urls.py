
from django.contrib import admin
from django.urls import path , include
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("" , views.home, name = "home" ),
    path("doctors_profile/<int:doctor_id>/" , views.doc_profile , name = 'doc_profile'),
    path("know_more/" ,views.know_more , name= "know_more" ),
    path("learn_more/" ,views.learn_more , name= "learn_more" ),
    path("expert_doctors/" , views.expert_doctors , name = "expert_doctors"),
    path("signup/" , views.sign_up , name="signup"),
    path("meds/" , include("meds.urls")),
    path("models/" , include("models.urls")),
    path('__reload__' , include('django_browser_reload.urls'))

    

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)