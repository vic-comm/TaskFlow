from django import forms
from django.shortcuts import reverse
from .utils import has_circular_template_task
from .models import WorkFlowTemplate, TemplateTask, TemplateDependency
from leads.models import Employee
class CreateWorkflowForm(forms.ModelForm):
    class Meta:
        model = WorkFlowTemplate
        fields = ['name', 'company', 'description']
        widgets = {'company': forms.Select(attrs={'class':"w-full px-4 py-3 bg-slate-900/60 border-2 border-slate-600 rounded-lg text-slate-100 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 focus:outline-none transition-all duration-300"}),}

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        if user and hasattr(user, 'employee'):
            self.fields['company'].initial = user.employee.company
            self.fields['company'].disabled = True

class TemplateTaskForm(forms.ModelForm):
    create_group_chat = forms.BooleanField(initial=False, required=False)
    class Meta:
        model = TemplateTask
        fields = ['title', 'description', 'assignee', 'duration']
        widgets = {'assignee':forms.CheckboxSelectMultiple()}
        
    def __init__(self, *args, **kwargs):
        workflow_template = kwargs.pop('template')
        super().__init__(*args, **kwargs)
        self.fields['assignee'].queryset = Employee.objects.filter(company=workflow_template.company)
        self.fields['assignee'].widget.attrs.update({
            'class': 'form-checkbox h-4 w-4 text-blue-600 transition duration-150 ease-in-out',
            'hx-post': reverse('workflow:htmx_check'),
            'hx-trigger': 'change',
            'hx-target': '#group-chat-toggle',
            'hx-include': 'closest form',
        })
        
class TemplateDependencyForm(forms.Form):
    from_template = forms.ModelChoiceField(queryset=TemplateTask.objects.none(),widget=forms.Select(attrs={'class': 'form-select bg-slate-700 text-white px-4 py-2 rounded-md'}), label='from task')
    to_template = forms.ModelChoiceField(queryset=TemplateTask.objects.none(), widget=forms.Select(attrs={'class': 'form-select bg-slate-700 text-white px-4 py-2 rounded-md'}), label='to task')
    dependency_type = forms.ChoiceField(choices=TemplateDependency.DEPENDENCY_TYPE, label="Select dependency",widget=forms.Select(attrs={'class': 'form-select bg-slate-700 text-white px-4 py-2 rounded-md'}))

    def __init__(self, *args, **kwargs):
        self.workflow_template = kwargs.pop('workflow_template')
        super().__init__(*args, **kwargs)
        template_queryset  =  TemplateTask.objects.filter(template__company=self.workflow_template.company)
        self.fields['from_template'].queryset = template_queryset
        self.fields['to_template'].queryset = template_queryset
        

        if self.is_bound and self.data.get('from_template'):
            try:
                self.fields['to_template'].queryset = template_queryset.exclude(id=int(self.data.get('from_template')))
            except (ValueError, TypeError):
                ... 


    def clean(self):
        cd = super().clean()
        current_template = cd.get('from_template')
        dependent_template = cd.get('to_template')

        if dependent_template and has_circular_template_task(current_template, dependent_template):
            raise forms.ValidationError("Circular dependency detected. This dependency cannot be created")
        return cd
        

