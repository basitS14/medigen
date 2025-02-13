import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Appointment, CustomUser

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        self.user_group_name = f"user_{self.user.id}"
        
        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.user_group_name,
            self.channel_name
        )

    @database_sync_to_async
    def get_appointment_doctor(self, appointment_id):
        try:
            appointment = Appointment.objects.get(id=appointment_id)
            return appointment.doctor.user.id
        except Appointment.DoesNotExist:
            return None

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type')
        
        if message_type == 'call_request':
            appointment_id = data['appointment_id']
            # Get doctor's user ID for this appointment
            doctor_user_id = await self.get_appointment_doctor(appointment_id)
            
            if doctor_user_id:
                # Send notification to doctor
                await self.channel_layer.group_send(
                    f"user_{doctor_user_id}",
                    {
                        "type": "call_notification",
                        "appointment_id": appointment_id,
                        "caller_id": self.user.id,
                        "caller_name": self.user.full_name
                    }
                )
        
        elif message_type == 'call_rejected':
            appointment_id = data['appointment_id']
            # Notify the caller that the call was rejected
            await self.channel_layer.group_send(
                f"user_{data['caller_id']}",
                {
                    "type": "call_rejected",
                    "appointment_id": appointment_id
                }
            )

    async def call_notification(self, event):
        await self.send(text_data=json.dumps({
            "type": "call_notification",
            "appointment_id": event["appointment_id"],
            "caller_id": event["caller_id"],
            "caller_name": event["caller_name"]
        }))

    async def call_rejected(self, event):
        await self.send(text_data=json.dumps({
            "type": "call_rejected",
            "appointment_id": event["appointment_id"]
        }))

    async def disconnect(self, close_code):
        # Remove from groups before disconnecting
        if hasattr(self, 'user_group_name'):
            await self.channel_layer.group_discard(
                self.user_group_name,
                self.channel_name
            )
        await super().disconnect(close_code)