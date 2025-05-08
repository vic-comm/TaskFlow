from django import forms
from .models import Task
from .models import User, Employee
from django.contrib.auth.forms import UserCreationForm, UsernameField

class TaskModelForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'start_date', 'end_date', 'employee']

class TaskForm(forms.Form):
    title = forms.CharField()
    description = forms.Textarea()
    start_date = forms.DateTimeField()
    end_date = forms.DateTimeField()

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username",)
        field_classes = {"username": UsernameField}

class AgentAssignForm(forms.Form):
    agent = forms.ModelChoiceField(queryset=Employee.objects.all())

class TaskUpdateCategoryForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['category']