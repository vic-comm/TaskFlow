import json
from channels.generic.websocket import WebsocketConsumer
from .models import ChatGroup, ChatMessage
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from asgiref.sync import async_to_sync

class ChatroomConsumer(WebsocketConsumer):
    def connect(self):
        self.user = self.scope['user']
        self.chatroom_name = self.scope['url_route']['kwargs']['group_name']
        self.chatroom = get_object_or_404(ChatGroup, group_name=self.chatroom_name)
        async_to_sync(self.channel_layer.group_add)(
            self.chatroom_name, self.channel_name
        )

        if self.user not in self.chatroom.users_online.all():
            self.chatroom.users_online.add(self.user)
            self.update_online_count()

        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.chatroom_name, self.channel_name
        )

        if self.user in self.chatroom.users_online.all():
            self.chatroom.users_online.remove(self.user)
            self.update_online_count()


    def receive(self, text_data=None):
        text_data_json = json.loads(text_data)
        body = text_data_json['body']
        message = ChatMessage.objects.create(author=self.user, body=body, group=self.chatroom)
        event = {
            'type': 'message_handler',
            'message_id': message.id
        }

        async_to_sync(self.channel_layer.group_send)(self.chatroom_name, event)

    def message_handler(self, event):
        message_id = event['message_id']
        message = get_object_or_404(ChatMessage, id=message_id)
        context = {'message':message, 'user':self.user, 'sent_by_me': self.user.id == message.author.id}
        html = render_to_string('chat/partials/chat_message_p.html', context=context)
        self.send(text_data=html)

    def update_online_count(self):
        online_count = self.chatroom.users_online.count() -1

        event = {'type': 'online_count_handler',
                 'online_count':online_count}
        async_to_sync(self.channel_layer.group_send)(self.chatroom_name, event)

    def online_count_handler(self, event):
        online_count = event['online_count']
        context = {'online_count':online_count, 'chat_group':self.chatroom}
        html = render_to_string('chat/partials/online_count.html', context)
        self.send(text_data=html)


class OnlineStatusConsumer(WebsocketConsumer):
    def connect(self):
        self.user = self.scope['user']
        self.groupchat_name = 'OnlineStatus'
        self.groupchat = get_object_or_404(ChatGroup, groupchat_name = self.groupchat_name)

        if self.user not in self.group.online_users.all():
            self.group.users_online.add(self.user)

        async_to_sync(self.channel_layer.group_add)(self.groupchat_name, self.channel_name)
        
        self.accept()
        self.online_status()

    def disconnect(self, close_code):
        if self.user in self.group.online_users.all():
            self.group.users_online.remove(self.user)

        async_to_sync(self.channel_layer.group_discard)(self.groupchat_name, self.channel_layer)
        self.online_status()
        

    def online_status(self):
        event = {'type':'online_status_handler'}
        async_to_sync(self.channel_layer.group_send)(self.groupchat_name, event)

    def online_status_handler(self, event):
        online_users = self.group.users_online.exclude(id=self.group.id)
        context = {'online_users':online_users}
        html =  render_to_string('chat/partials/online_users.html', context=context)

        return self.send(text_data=html)

