from .consumers import ChatroomConsumer, OnlineStatusConsumer
from django.urls import path


websocket_urlpatterns = [path('ws/chatroom/<group_name>/', ChatroomConsumer.as_asgi()),
                         path('ws/online-status/', OnlineStatusConsumer.as_asgi()),]