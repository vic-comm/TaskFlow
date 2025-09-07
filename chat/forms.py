from django.forms import Form, ModelForm
from django import forms
from .models import ChatMessage, ChatGroup

class ChatMessageForm(ModelForm):
    class Meta:
        model = ChatMessage
        fields = ['body']
        # widgets = {'body': forms.TextInput(attrs={'placeholder': 'Add message ...', 'class':'p-4 text-black', 'autofocus':True})}
        # widget=forms.TextInput(attrs={"placeholder": "Type a message...",
        #                     "class": "flex-1 bg-gray-700 text-gray-200 placeholder-gray-400 rounded-xl px-4 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"})
        widgets = {
    'body': forms.Textarea(attrs={
        'id': 'id_body',
        'placeholder': 'Type your message...',
        'class': 'w-full px-4 py-3 pr-12 bg-gray-700 text-white placeholder-gray-400 rounded-xl border border-gray-600 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 resize-none transition-all duration-200',
        'rows': 1,
        'autofocus': True,
        'style': 'min-height: 48px; max-height: 120px;',
        '_': 'on keydown if event.key is "Enter" and not event.shiftKey halt the event then trigger submit on the closest form'
    })
}
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