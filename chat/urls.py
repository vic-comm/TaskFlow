from django.urls import path
from . import views
app_name='chat'
urlpatterns = [
    path('chat/<str:group_name>/', views.chat_home, name='chat'),
    path('chat/<user_name>/', views.get_or_create_chatroom, name='start_chat'),
    path('chat/new_groupchat/', views.create_group_chat, name='create_groupchat'),
    path('chat/edit/<chatroom_name>/', views.edit_chat, name='edit-chatroom'),
    path('chat/delete/<chatroom_name>/', views.delete_chatroom, name='chatroom-delete'),
    path('chat_file_upload/<group_name>/', views.chat_file_upload, name='chat_file_upload'),
]
