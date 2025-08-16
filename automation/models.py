from django.db import models
from django.utils import timezone
from django.conf import settings
# from leads.models import Employee, Company, Task
# Create your models here.

class WorkFlowTemplate(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField()
    company = models.ForeignKey('leads.Company', on_delete=models.CASCADE)
    created_by = models.ForeignKey('leads.Employee', on_delete=models.SET_NULL, null=True)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class TemplateTask(models.Model):
    template = models.ForeignKey(WorkFlowTemplate, related_name='template_tasks', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    status = models.CharField(choices=[('completed', 'Completed'),('pending', 'Pending'), ('suspended', 'Suspended')], default='pending', max_length=40)
    assignee = models.ManyToManyField('leads.Employee', blank=True, help_text="Optional: employees to assign this task to by default")
    chat_group = models.BooleanField(default=False)
    duration = models.PositiveIntegerField(default=3)
    def __str__(self):
        return self.title


class TemplateDependency(models.Model):
    DEPENDENCY_TYPE = [
            ('finish_to_start', 'Finish to Start'),
            ('start_to_start', 'Start to Start'),
            ('finish_to_finish', 'Finish to Finish'),
            ('start_to_finish', 'Start to Finish'),
        ]
    from_task = models.ForeignKey(TemplateTask, related_name='template_successors', on_delete=models.CASCADE)
    to_task = models.ForeignKey(TemplateTask, related_name='template_predecessors', on_delete=models.CASCADE)
    dependency_type = models.CharField(
        max_length=30,
        choices=DEPENDENCY_TYPE
    )

    def __str__(self):
       return f"{self.from_task.title} → {self.to_task.title} ({self.dependency_type})"