import json
from channels.generic.websocket import AsyncWebsocketConsumer

class LiveFeedConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = 'post_feed'
        await self.channel_layer.group_add(
            self.room_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # This is optional if you want clients to send messages
        pass

    async def send_update(self, event):
        # Send a new post update to the WebSocket
        await self.send(text_data=json.dumps({
            'content': event['content'],
            'timestamp': event['timestamp'],
        }))
