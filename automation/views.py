from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from .forms import CreateWorkflowForm, TemplateTaskForm, TemplateDependencyForm
from .models import WorkFlowTemplate, TemplateTask, TemplateDependency
from django.contrib.auth.decorators import login_required
from django.forms import formset_factory
from .utils import generate_workflow
from django.template.loader import render_to_string
# Create your views here.
@login_required
def workflow_list(request):
    workflows = WorkFlowTemplate.objects.filter(company=request.user.employee.company)

    if request.method == 'POST':
        form = CreateWorkflowForm(request.POST, user=request.user)
        if form.is_valid():
            workflow = form.save(commit=False)
            workflow.created_by = request.user.employee
            workflow.save()
            return redirect('workflow:workflow_list')
    else:
        form = CreateWorkflowForm(user=request.user)
    
    return render(request, 'automation/workflow_list.html', {'workflows':workflows, 'form':form})

def create_template_task(request, workflow_id):
    workflow = get_object_or_404(WorkFlowTemplate, id=workflow_id)
    if request.method == 'POST':
        form = TemplateTaskForm(request.POST, template=workflow)
        if form.is_valid():
            create_group = form.cleaned_data['create_group_chat']
            assignee = form.cleaned_data['assignee']
            task = form.save(commit=False)
            task.status = 'pending'
            task.created_by = request.user.employee
            task.template = workflow
            if create_group:
                task.chat_group = True
            task.save()
            task.assignee.set(list(assignee))
            

        return redirect('workflow:workflow_detail', workflow.id)
    else:
        template_form = TemplateTaskForm(template=workflow)
    return render(request, 'automation/workflow_detail.html', {'template_form':template_form})


def assign_template_dependency(request, workflow_id):
    workflow_template = get_object_or_404(WorkFlowTemplate, id=workflow_id)
    if request.method == 'POST':
        dependency_form= TemplateDependencyForm(request.POST, workflow_template=workflow_template)
        if dependency_form.is_valid():
            cd = dependency_form.cleaned_data
            from_task = cd['from_template']
            to_task = cd['to_template']
            TemplateDependency.objects.create(from_task=from_task, to_task=to_task, dependency_type=cd['dependency_type'])
            return redirect('workflow:workflow_detail', workflow_template.id)
    else:
        dependency_form  = TemplateDependencyForm(workflow_template=workflow_template)
    return render(request, 'automation/workflow_detail.html', {'dependency_form':dependency_form})

def deploy_workflow(request, workflow_id):
    workflow = get_object_or_404(WorkFlowTemplate, id=workflow_id)
    if workflow.company != request.user.employee.company:
        return redirect('workflow:workflow_list')
    generate_workflow(workflow, workflow.company, request.user.employee)
    workflow.is_active = True
    workflow.save()
    return redirect('workflow:workflow_list')

def workflow_detail(request, workflow_id):
    workflow = get_object_or_404(WorkFlowTemplate, id=workflow_id)
    template_form = TemplateTaskForm(template=workflow)
    template_tasks = TemplateTask.objects.filter(template=workflow)
    dependency_form= TemplateDependencyForm(request.POST, workflow_template=workflow)

    dependencies = TemplateDependency.objects.filter(to_task__template=workflow, from_task__template=workflow).select_related('from_task', 'to_task')
    return render(request, 'automation/workflow_detail.html', {'workflow':workflow, 'template_tasks':template_tasks, 'dependencies':dependencies, 'dependency_form':dependency_form, 'template_form':template_form})

def htmx_check_create_group_chat(request):
    assigned_ids = request.POST.getlist('assignee')
    if len(assigned_ids) >= 2:
        html = render_to_string('leads/partials/group_chat_toggle.html')
    else:
        html = ''  # Return empty so the checkbox disappears
    return HttpResponse(html)

def delete_template(request, workflow_id, task_id):
    if request.POST:
        template = TemplateTask.objects.get(id=task_id)
        template.delete()
    return redirect('workflow:workflow_detail', workflow_id)

def delete_workflow(request, workflow_id):
    if request.method == 'POST':
        workflow = get_object_or_404(WorkFlowTemplate, id=workflow_id)
        workflow.delete()
    return redirect('workflow:workflow_list')