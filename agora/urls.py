from django.urls import path , include
from . import views

app_name="agora"

urlpatterns = [
    path(' ', views.index, name='agora-index'),
    path('pusher/auth/', views.pusher_auth, name='agora-pusher-auth'),
    path('token/', views.generate_agora_token, name='agora-token'),
    path('call-user/', views.call_user, name='agora-call-user'),
    path('__reload__' , include('django_browser_reload.urls'))

]