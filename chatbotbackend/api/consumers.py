from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from asgiref.sync import async_to_sync
import json
from .models import UserProfile
import base64

def nice_bytes(x):
    units = ['bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']
    n = int(x) if x else 0
    l = 0

    while n >= 1024 and l < len(units) - 1:
        n /= 1024
        l += 1

    return f"{n:.1f} {units[l]}" if n < 10 and l > 0 else f"{int(n)} {units[l]}"

        
class AsyncConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        
        user_id = self.scope['query_string'].decode('utf-8').split('=')[1]
        
        if user_id:
            await self.channel_layer.group_add(
                f'user_{user_id}',
                self.channel_name
            )

            await self.accept()
            await self.update_user_status(user_id, 'online')
            
            await self.send_json({'message': f'Connected to WebSocket for User: {user_id}'})
        else:
            
            await self.close()
    
    
    async def receive(self, text_data):
        user_id = self.scope['query_string'].decode('utf-8').split('=')[1]
        json_text = json.loads(text_data)
        msg_type = json_text['type']
        sender_id = json_text['sender_id']
        receiver_id = json_text['receiver_id']
        message = json_text['message']
        sender_name = json_text['sender_name']
        receiver_name = json_text['receiver_name']

        if(msg_type == 'File Message'):

            fileURL = json_text['fileURL']
            fileSize = json_text['fileSize']
            await self.channel_layer.group_send(
            f'user_{receiver_id}',
            {
            "type": "receiveFile",
            'message': message,
            'sender_name': sender_name,
            'receiver_name': receiver_name,
            'sender_id': sender_id,
            'receiver_id': receiver_id,
            'fileURL': fileURL,
            'fileSize': fileSize,
        }
        )
        
        else:
            await self.channel_layer.group_send(
                f'user_{receiver_id}',
                {
                "type": "receiveMessage",
                'message': message,
                'sender_name': sender_name,
                'receiver_name': receiver_name,
                'sender_id': sender_id,
                'receiver_id': receiver_id
            }
            )


    async def disconnect(self , close_code):
        user_id = self.scope['query_string'].decode('utf-8').split('=')[1]
        await self.channel_layer.group_discard(
            f'user_{user_id}', 
            self.channel_layer 
        )
        print("Im in Disconnect")
        await self.update_user_status(user_id, 'offline')

    # async def send_notification(self, event):
    #     print("in notification")
    #     # print(event)
    #     messageType = event['messageType']
    #     message = event['message']
    #     sender_id = event['sender_id']
    #     receiver_id = event['receiver_id']
    #     receiver_name = event['receiver_name']
    #     sender_name = event['sender_name']

    #     await self.send(text_data=json.dumps({
    #         'messageType': messageType,
    #         'message': message,
    #         'sender_id': sender_id,
    #         'receiver_id': receiver_id,
    #         'receiver_name': receiver_name,
    #         'sender_name': receiver_name,
    #     }))
    #     print(f"Notification sent to {receiver_name} by {sender_name}")


    async def receiveMessage(self,event):
        message = event['message']
        sender_id = event['sender_id']
        receiver_id = event['receiver_id']
        receiver_name = event['receiver_name']
        sender_name = event['sender_name']
        # receiver_id = event['receiver_id']

        await self.send(text_data=json.dumps({
            'message': message,
            'sender_id': sender_id,
            'receiver_id': receiver_id,
            'receiver_name': receiver_name,
            'sender_name': receiver_name,
        }))
        print(f"last message received by {receiver_id}")

    async def receiveFile(self,event):
        message = event['message']
        sender_id = event['sender_id']
        receiver_id = event['receiver_id']
        receiver_name = event['receiver_name']
        sender_name = event['sender_name']
        fileURL = event['fileURL']
        fileSize = event['fileSize']
        # receiver_id = event['receiver_id']

        await self.send(text_data=json.dumps({
            'type': 'File',
            'fileURL': fileURL,
            'fileSize': nice_bytes(fileSize),
            'message': message,
            'sender_id': sender_id,
            'receiver_id': receiver_id,
            'receiver_name': receiver_name,
            'sender_name': receiver_name,
        }))
        print(f"File received by {receiver_id}")
    
    @database_sync_to_async
    def update_user_status(self, user_id, status):
       
        return UserProfile.objects.filter(user_id=user_id).update(status=status)