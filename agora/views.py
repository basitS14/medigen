import os
import time
import json

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from dotenv import load_dotenv
from .agora_key.RtcTokenBuilder import RtcTokenBuilder, Role_Attendee
from pusher import Pusher
from meds.models import CustomUser

load_dotenv()

# Instantiate a Pusher Client
pusher_client = Pusher(
    app_id=os.getenv('app_id'),
    key=os.getenv('key'),
    secret=os.getenv('secret'),
    ssl=True,
    cluster=os.getenv('cluster')
)

@login_required(login_url='/admin/')
def index(request):
    all_users = CustomUser.objects.exclude(id=request.user.id).only('id', 'full_name')
    return render(request, 'agora/index.html', {'allUsers': all_users})

def pusher_auth(request):
    payload = pusher_client.authenticate(
        channel=request.POST['channel_name'],
        socket_id=request.POST['socket_id'],
        custom_data={
            'user_id': str(request.user.id),  # Make sure this is a string
            'user_info': {
                'id': request.user.id,
                'name': request.user.full_name
            }
        }
    )
    return JsonResponse(payload)

def generate_agora_token(request):
    appID = os.getenv('AGORA_APP_ID')
    appCertificate = os.getenv('AGORA_APP_CERTIFICATE')
    body = json.loads(request.body.decode('utf-8'))
    channelName = body['channelName']
    userAccount = request.user.email
    expireTimeInSeconds = 3600
    currentTimestamp = int(time.time())
    privilegeExpiredTs = currentTimestamp + expireTimeInSeconds

    token = RtcTokenBuilder.buildTokenWithAccount(
        appID, appCertificate, channelName, userAccount, Role_Attendee, privilegeExpiredTs
    )
    return JsonResponse({'token': token, 'appID': appID})

def call_user(request):
    body = json.loads(request.body.decode('utf-8'))
    user_to_call = body['user_to_call']
    channel_name = body['channel_name']
    caller = request.user.email

    pusher_client.trigger(
        'presence-online-channel',
        'make-agora-call',
        {
            'userToCall': user_to_call,
            'channelName': channel_name,
            'from': caller
        }
    )
    return JsonResponse({'message': 'Call has been placed'})