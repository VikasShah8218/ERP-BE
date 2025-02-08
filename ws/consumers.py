from channels.generic.websocket import AsyncWebsocketConsumer
import json

class MyWebSocketConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("broadcast_group", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("broadcast_group",self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        print("Received message:", data)

    async def send_message(self, event):
        message = event["message"]
        await self.send(text_data=json.dumps({"message": message}))


