from django.db import models
from leads.models import Task
from django.contrib.auth import get_user_model
import shortuuid
from PIL import Image
from cloudinary_storage.storage import MediaCloudinaryStorage, RawMediaCloudinaryStorage
import mimetypes
import os
# User = get_user_model()
from django.conf import settings
# Create your models here.
def generate_uuid():
    return shortuuid.uuid()

class ChatGroup(models.Model):
    group_name = models.CharField(unique=True, default=generate_uuid)
    users_online = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='online_in_groups', blank=True)
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='chat_groups', blank=True)
    is_private = models.BooleanField(default=False)
    admin = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name='groupchats', blank=True, null=True)
    groupchat_name = models.CharField(unique=True, blank=True, null=True)
    task = models.OneToOneField(Task, on_delete=models.CASCADE, related_name='group_chat')

    def __str__(self):
        return self.groupchat_name
    
class ChatMessage(models.Model):
    group = models.ForeignKey(ChatGroup, on_delete=models.CASCADE, related_name='chat_message')
    body = models.TextField(null=True, blank=True)
    file = models.FileField(upload_to='files/', storage=RawMediaCloudinaryStorage(), blank=True, null=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    @property
    def filename(self):
        if self.file:
            return os.path.basename(self.file.name)
        else:
            return None
        
    # @property
    # def is_image(self):
    #     try:
    #         image = Image.open(self.file)
    #         image.verify()
    #         return True
    #     except:
    #         return False
    @property
    def is_image(self):
        if not self.file:
            return False
        mime_type, _ = mimetypes.guess_type(self.file.name)
        return mime_type and mime_type.startswith("image")
    
    def __str__(self):
        if self.body:
            return f'{self.author.username} : {self.body}'
        elif self.file:
            return f'{self.author.username} : {self.filename}'
        
    class Meta:
        ordering = ['-created']