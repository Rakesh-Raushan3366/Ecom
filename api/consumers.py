import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

# Assuming we have a Django model Order
class OrderConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope["user"]
        # Only allow authenticated users to connect
        if user.is_anonymous:
            await self.close()
            return
        self.group_name = f"user_{user.id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    # Handle disconnection
    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    # Receive message from WebSocket
    async def order_notification(self, event):
        payload = {
            "type": "order_update",
            "order_id": event["order_id"],
            "status": event["status"],
        }
        await self.send(text_data=json.dumps(payload))
