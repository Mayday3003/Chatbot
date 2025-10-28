import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.session_id = self.scope['url_route']['kwargs']['session_id']
        self.group_name = f'chat_{self.session_id}'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        text = data.get('text')
        if not text:
            return
        # call sync view logic to handle message and produce bot_text
        from .views import SendMessageView
        # emulate request
        class DummyReq:
            data = {'session_id': self.session_id, 'text': text}
        resp = await sync_to_async(SendMessageView().post)(DummyReq())
        # resp is DRF Response; extract data
        bot_text = resp.data.get('bot') if hasattr(resp, 'data') else 'error'
        # broadcast both user and bot messages
        await self.channel_layer.group_send(self.group_name, {
            'type': 'chat.message',
            'message': {'sender': 'user', 'text': text}
        })
        await self.channel_layer.group_send(self.group_name, {
            'type': 'chat.message',
            'message': {'sender': 'bot', 'text': bot_text}
        })

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event['message']))
