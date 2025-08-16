from django.forms import Form, ModelForm
from django import forms
from .models import ChatMessage, ChatGroup

class ChatMessageForm(ModelForm):
    class Meta:
        model = ChatMessage
        fields = ['body']
        widgets = {'body': forms.TextInput(attrs={'placeholder': 'Add message ...', 'class':'p-4 text-black', 'autofocus':True})}

class ChatGroupForm(ModelForm):
    class Meta:
        model = ChatGroup
        fields = ['groupchat_name']
        widgets = {'groupchat_name': forms.TextInput(attrs={
            'placeholder':'Add name...',
            'class':'p-4 text-black', 'autofocus':True
        })}

class EditChatGroupForm(ModelForm):
    class Meta:
        model = ChatGroup
        fields = ['groupchat_name']
        widgets = {'groupchat_name': forms.TextInput(attrs={
            'placeholder':'Add name...',
            'class':'p-4 text-black', 'autofocus':True
        })}