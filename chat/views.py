from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import ChatGroup, ChatMessage
from .forms import ChatMessageForm, ChatGroupForm, EditChatGroupForm
from django.http import Http404
from channels.layers import get_channel_layer
from django.contrib import messages
from django.contrib.auth import get_user_model
from asgiref.sync import async_to_sync

# Create your views here.
def chat_home(request, group_name):
    chat_group = get_object_or_404(ChatGroup, group_name=group_name)
    messages = chat_group.chat_message.all()
    # if request.method == 'GET':
    #     form = ChatMessageForm()
    #     return render(request, 'chat.html', {"messages":messages, 'form':form})
    # else:
    #     form = ChatMessageForm(request.POST)
    #     if form.is_valid:
    #         message = form.save(commit=False)
    #         message.author = request.user
    #         message.group = chat_group
    #         message.save()
    #     return redirect('chat:chat')
    other_user = None
    if chat_group.is_private:
        if request.user not in chat_group.members.all():
            return Http404()
        for member in chat_group.members.all():
            if member != request.user:
                other_user = member
                break

    if chat_group.groupchat_name:
        if request.user not in chat_group.members.all():
            chat_group.members.add(request.user)

    if request.htmx:
        form = ChatMessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.author = request.user
            message.group = chat_group
            message.save()
            context = {'message':message, 'user':request.user}
            return render(request, 'chat/partials/chat_message_p.html', context)
        
    form = ChatMessageForm()
    return render(request, 'chat/chat.html', {"messages":messages, 'form':form, 'group_name':group_name, 'other_user':other_user, 'chat_group':chat_group, 'user':request.user})

def get_or_create_chatroom(request, username):
    User = get_user_model()
    if request.user.username == username:
        redirect('leads:')
    other_user = User.objects.get(username=username)
    my_chatrooms = request.user.chat_groups.filter(is_private=True)

    if my_chatrooms:
        for chatroom in my_chatrooms:
            if other_user in chatroom.members.all():
                chatroom = chatroom
                break
    else:
        chatroom = ChatGroup.objects.create(is_private=True)
        chatroom.members.add(request.user, other_user)

    return redirect('chat:chat', chatroom.group_name)

def create_group_chat(request):
    if request.method == 'POST':
        form = ChatGroupForm(request.POST)
        if form.is_valid():
            new_group = form.save(commit=False)
            new_group.admin = request.user
            new_group.save()
            new_group.members.add(request.user)          
            return redirect('chat:chat', new_group.groupchat_name)
    form =  ChatGroupForm()
    return render(request, 'chat/group_chat.hml', {'form':form})

def edit_chat(request, group_name):
    chat_group = ChatGroup.objects.get(group_name=group_name)
    if request.user != chat_group.admin:
        raise Http404()

    if request.method == 'POST':
        form = EditChatGroupForm(request.POST)
        if form.is_valid():
            form.save()

            remove_list = request.POST.getlist('remove_members')
            for member in remove_list:
                chat_group.members.remove(member)

            return redirect('chat:chat_room', group_name)
    form = EditChatGroupForm(instance=chat_group)
    context = {'form':form, 'chat_group':chat_group}
    return render(request, 'chat/edit_chatroom.html', context)

def delete_chatroom(request, chatroom_name):
    chat_group = ChatGroup.objects.get(group_name=chatroom_name)

    if request.user != chat_group.admin:
        raise Http404()
    
    if request.method == 'POST':
        chat_group.delete()
        messages.success("Chat room deleted")
        return redirect('leads:')
    return render(request, 'chat/delete_chat.html', {'chat_group':chat_group})


def chat_file_upload(request, group_name):
    chat_group = ChatGroup.objects.get(group_name=group_name)

    if request.htmx and request.FILES:
        file = request.FILES['file']
        message = ChatMessage.objects.create(author=request.user, file=file, group=chat_group)
        channel_layer = get_channel_layer()
        event = {'type':'message_handler', 'message_id':message.id}
        async_to_sync(channel_layer.group_send)(chat_group.group_name, event)
        return HttpResponse()
