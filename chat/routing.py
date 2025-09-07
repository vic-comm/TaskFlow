from .consumers import ChatroomConsumer, OnlineStatusConsumer
from django.urls import re_path


# websocket_urlpatterns = [path('ws/chatroom/<group_name>/', ChatroomConsumer.as_asgi()),
#                          path('ws/online-status/', OnlineStatusConsumer.as_asgi()),]

websocket_urlpatterns = [
    re_path(r'ws/chatroom/(?P<group_name>\w+)/$', ChatroomConsumer.as_asgi()),
    re_path(r'ws/online-status/$', OnlineStatusConsumer.as_asgi()),
]