from django import forms
from .models import Task
from .models import User, Employee, Company, TaskDocuments, TaskDependency
from django.contrib.auth.forms import UserCreationForm, UsernameField
from django.urls import reverse
from .utils import has_circular_task

class TaskDocumentForm(forms.ModelForm):
    class Meta:
        model = TaskDocuments
        fields = ['file', 'file_name']
        widgets = {
            'file_name': forms.TextInput(attrs={
                'class': 'block w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500',
                'placeholder': 'Enter a descriptive file name'
            }),
            'file': forms.ClearableFileInput(attrs={
                'class': 'block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100',
                'placeholder': "Upload task document"
            }),
        }

class TaskModelForm(forms.ModelForm):
    create_group_chat = forms.BooleanField(required=False, initial=True)
    class Meta:
        model = Task
        fields = ['title', 'description', 'start_date', 'end_date', 'assigned_to', 'create_group_chat']
        widgets = {'assigned_to':forms.CheckboxSelectMultiple, 'start_date':forms.DateInput(attrs={'type':'date', 'required':True}),  'end_date':forms.DateInput(attrs={'type':'date', 'required':True})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['assigned_to'].widget.attrs.update({
            'class': 'form-checkbox h-4 w-4 text-blue-600 transition duration-150 ease-in-out',
            'hx-post': reverse('leads:htmx_check'),
            'hx-trigger': 'change',
            'hx-target': '#group-chat-toggle',
            'hx-include': 'closest form',
        })




class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username",'first_name', 'last_name', 'email', 'avatar')
        field_classes = {"username": UsernameField}


class AgentAssignForm(forms.Form):
    agent = forms.ModelMultipleChoiceField(queryset=Employee.objects.all(), widget=forms.CheckboxSelectMultiple)
    


class CompanyModelForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['name', 'logo']

class AssignTaskDependencyForm(forms.Form):
    from_task = forms.ModelChoiceField(queryset=Task.objects.none(),widget=forms.Select(attrs={'class': 'form-select bg-slate-700 text-white px-4 py-2 rounded-md'}), label='from task')
    to_task = forms.ModelChoiceField(queryset=Task.objects.none(),widget=forms.Select(attrs={'class': 'form-select bg-slate-700 text-white px-4 py-2 rounded-md'}), label='to task')
    dependency_type = forms.ChoiceField(choices=TaskDependency.DEPENDENCIES,label= 'select peculiar dependency',widget=forms.Select(attrs={'class': 'form-select bg-slate-700 text-white px-4 py-2 rounded-md'}))
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        queryset = Task.objects.filter(company=self.user.employee.company)
        self.fields['from_task'].queryset = queryset
        self.fields['to_task'].queryset = queryset


    def clean(self):
        cd = self.cleaned_data
        from_task = cd['from_task']
        to_task = cd['to_task']
        if to_task and has_circular_task(from_task, to_task):
            raise forms.ValidationError("Circular dependency noticed.This dependency cannot be created")
        return cd
    

        