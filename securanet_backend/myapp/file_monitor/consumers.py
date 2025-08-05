from channels.generic.websocket import AsyncWebsocketConsumer
import json

class FileMonitorConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("file_monitor", self.channel_name)
        await self.accept()
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("file_monitor", self.channel_name)
    
    async def notify_analysis(self, event):
        await self.send(text_data=json.dumps(event["data"]))