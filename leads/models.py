from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
# Create your models here.
class User(AbstractUser):
    is_organisor = models.BooleanField(default=False)
    is_agent = models.BooleanField(default=True)

class Task(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    employee = models.ForeignKey('Employee', on_delete=models.SET_NULL, blank=True, null=True)
    profile = models.ForeignKey('UserProfile', on_delete=models.CASCADE, blank=True, null=True)
    category = models.ForeignKey('Category', related_name='tasks', on_delete=models.SET_NULL, blank=True, null=True)


    def __str__(self):
        return f'{self.title}'
    

class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile = models.ForeignKey('UserProfile', on_delete=models.CASCADE)
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"
    
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    

    def __str__(self):
        return self.user.username

def post_user_created_signal(sender, created, instance, **kwargs):
    print(instance, created)
    if created:
        UserProfile.objects.create(user=instance)

post_save.connect(post_user_created_signal, sender=User)

class Category(models.Model):
    name = models.CharField(max_length=30)
    profile = models.ForeignKey('UserProfile', on_delete=models.CASCADE)

    def __str__(self):
        return self.name