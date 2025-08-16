from django.db import models
from django.shortcuts import reverse
from django.contrib.auth.models import AbstractUser
from automation.models import WorkFlowTemplate
# Create your models here.
class User(AbstractUser):
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.username

class TaskDocuments(models.Model):
    task = models.ForeignKey('Task', on_delete=models.CASCADE, related_name='documents')
    file_name = models.CharField(max_length=150, blank=True, null=True)
    file = models.FileField(upload_to='task_documents/', null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.file_name} for {self.task.title}"

class Task(models.Model):
    STATUS = [('completed', 'Completed'),('pending', 'Pending'), ('suspended', 'Suspended'), ('pending_approval', 'Pending_approval')]
    title = models.CharField(max_length=50)
    description = models.TextField()
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    assigned_to = models.ManyToManyField('Employee', blank=True, related_name='assigned_task')
    created_by = models.ForeignKey('Employee', related_name='created_tasks', on_delete=models.SET_NULL, null=True)
    company = models.ForeignKey('Company', on_delete=models.CASCADE, blank=True, null=True, related_name='tasks')
    # group_chat = models.OneToOneField('chat.ChatGroup, blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    status = models.CharField(choices=STATUS, max_length=20, null=True, blank=True, default='pending')
    requires_approval = models.BooleanField(default=False)
    create_group_chat = models.BooleanField(default=False, null=True, blank=True)
    workflow = models.ForeignKey(WorkFlowTemplate, null=True, blank=True, related_name='workflow_tasks', on_delete=models.SET_NULL)

    def get_absolute_url(self):
        return reverse("task_detail", kwargs={"pk": self.pk})
    
    def is_blocked(self):
        if self.status == 'suspended':
            return True
        return False
    
    def __str__(self):
        return self.title
    

class Employee(models.Model):
    ROLES = (('employee', 'Employee'), ("manager", "Manager"))
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company = models.ForeignKey('Company', on_delete=models.CASCADE, related_name='employees')
    role = models.CharField(choices=ROLES, max_length=20)
    date_joined = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} ({self.role} @ {self.company.name})"
    
class Company(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='company')
    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    logo = models.ImageField(upload_to='logos/', blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    

    def __str__(self):
        return self.name



class Category(models.Model):
    name = models.CharField(max_length=30)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
    
class TaskDependency(models.Model): 
    DEPENDENCIES = (('start_to_finish', 'Start to finish'), ('start_to_start', 'Start to start'), ('finish_to_finish', 'Finish to finish'), ('finish_to_start', 'Finish to start'))
    from_task = models.ForeignKey(Task, related_name='dependent_tasks', on_delete=models.CASCADE)
    to_task = models.ForeignKey(Task, related_name='blocking_tasks', on_delete=models.CASCADE)
    dependency_type = models.CharField(choices=DEPENDENCIES, max_length=40)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
