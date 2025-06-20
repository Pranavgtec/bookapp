import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async  # <-- IMPORT THIS
from django.contrib.auth import get_user_model  # <-- IMPORT THIS

# Import your models from the same app (assuming Inquiry and InquiryMessage are in ecommerceapp/models.py)
from .models import Inquiry, InquiryMessage  # <-- IMPORT YOUR MODELS

User = get_user_model()  # Get the User model configured in Django

class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.inquiry_id = self.scope['url_route']['kwargs']['inquiry_id']
        self.room_group_name = f"inquiry_{self.inquiry_id}"

        # Add consumer to the group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave group on disconnect
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_content = data['message']  # Renamed 'message' to 'message_content' to be distinct
        current_user = self.scope["user"]  # Get the currently authenticated user

        # --- 1. Save message to database ---
        try:
            # Fetch the Inquiry instance
            inquiry_instance = await self.get_inquiry_instance(self.inquiry_id)

            # Create and save the InquiryMessage instance
            await self.save_message_to_db(
                inquiry=inquiry_instance,
                sender=current_user,
                content=message_content
            )
        except Inquiry.DoesNotExist:
            print(f"Error: Inquiry with ID {self.inquiry_id} not found when saving message.")
            await self.send(text_data=json.dumps({"error": "Inquiry not found for message saving."}))
            return  # Stop processing if inquiry doesn't exist
        except Exception as e:
            print(f"CRITICAL ERROR saving message to DB: {e}")
            # You might want to log this error more formally
            await self.send(text_data=json.dumps({"error": "Failed to save message."}))
            return

        # --- 2. Broadcast the message to the group (including sender info) ---
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message_content,
                'sender_id': current_user.id,  # Pass sender's ID
                'sender_username': current_user.username,  # Pass sender's username
                'sender_display_name': current_user.get_full_name() or current_user.username,  # For display in frontend
            }
        )

    async def chat_message(self, event):
        # This method receives the message from the channel layer and sends it to the WebSocket
        message = event['message']
        sender_id = event['sender_id']
        sender_username = event['sender_username']
        sender_display_name = event['sender_display_name']

        await self.send(text_data=json.dumps({
            'message': message,
            'sender_id': sender_id,
            'sender_username': sender_username,
            'sender_display_name': sender_display_name
        }))

    # --- Helper methods for database operations (MUST be outside the main async methods) ---

    @database_sync_to_async
    def get_inquiry_instance(self, inquiry_id):
        # We use .get() which will raise DoesNotExist if not found
        return Inquiry.objects.get(id=inquiry_id)

    @database_sync_to_async
    def save_message_to_db(self, inquiry, sender, content):
        # Ensure 'inquiry', 'sender', and 'content' match your InquiryMessage model fields
        return InquiryMessage.objects.create(
            inquiry=inquiry,
            sender=sender,
            content=content
        )