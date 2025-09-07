from django.db import models
from django.utils import timezone
from django.conf import settings
from django.core.exceptions import ValidationError
from .utils import has_circular_template_task
# from leads.models import Employee, Company, Task
# Create your models here.

class WorkFlowTemplate(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField(null=True, blank=True)
    company = models.ForeignKey('leads.Company', on_delete=models.CASCADE)
    created_by = models.ForeignKey('leads.Employee', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=False)
    last_deployed = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name

class TemplateTask(models.Model):
    template = models.ForeignKey(WorkFlowTemplate, related_name='template_tasks', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    status = models.CharField(choices=[('completed', 'Completed'),('pending', 'Pending'), ('suspended', 'Suspended')], default='suspended', max_length=40)
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
    
    def clean(self):
        if self.from_task == self.to_task:
            raise ValidationError("A task cannot depend on its self")
        elif has_circular_template_task(self.from_task, self.to_task):
            raise ValidationError("Circular dependency detected")
        
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

class WorkflowInstance(models.Model):
    template = models.ForeignKey(WorkFlowTemplate, on_delete=models.CASCADE, related_name='instance')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(choices=[("draft","Draft"),("active","Active"),("completed","Completed")],max_length=20,default="active")
    created_by = models.ForeignKey('leads.Employee', on_delete=models.SET_NULL, null=True)
    company = models.ForeignKey('leads.Company', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.template.name} - {self.status}"

