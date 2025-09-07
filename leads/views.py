from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.utils import timezone
from .models import Task, Employee, TaskDependency
from django.core.mail import send_mail
from .forms import TaskModelForm, TaskDocumentForm, AssignTaskDependencyForm
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import CustomUserCreationForm, AgentAssignForm,  CompanyModelForm
from django.views import generic
from employees.mixins import CustomLoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.contrib.auth import login
from django.utils.timezone import now
from datetime import timedelta
from django.db.models import Q, Count, Avg
from django.contrib import messages
# Create your views here.

class TaskListView(LoginRequiredMixin, ListView):
    template_name = 'leads/list1.html'
    context_object_name = 'task_list'

    def get_queryset(self):
        user = self.request.user
        employee = Employee.objects.get(user=user)
        queryset = Task.objects.filter(assigned_to__in=[employee], company=employee.company)
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        employee = Employee.objects.get(user=self.request.user)
        context['employee'] = employee
        context['chat_groups'] = self.request.user.chat_groups
        if employee.role == 'manager':
            queryset = Task.objects.filter(assigned_to__isnull = True)
            context.update({'unassigned': queryset})
            queryset2 = Task.objects.filter(status='suspended')
            context.update({'suspended': queryset2})
            queryset3 = Task.objects.filter(assigned_to__isnull = False).exclude(status ='suspended').distinct()
            context.update({'active':queryset3.count()})
            queryset4 = Task.objects.filter(status='completed')
            queryset5 = Task.objects.filter(status='pending_approval')
            context.update({'active_tasks':queryset3, 'completed_tasks':queryset4, 'tasks_pending_approval':queryset5})
        return context

class TaskDetailView(LoginRequiredMixin, DetailView):
    template_name = 'leads/detail.html'
    context_object_name = 'task'

    def get_queryset(self):
        user = self.request.user
        employee = Employee.objects.get(user=user)
        if employee.role == 'manager':
            queryset = Task.objects.filter(company=employee.company)
        else:
            queryset = Task.objects.filter(assigned_to=employee, company=employee.company)
        return queryset
    
class TaskCreateView(CustomLoginRequiredMixin, generic.View):
    template_name = 'leads/create.html'

    def get(self, request, *args, **kwargs):
        task_form = TaskModelForm()
        document_form = TaskDocumentForm()

        return render(request, self.template_name, {"task_form":task_form, 'document_form':document_form})
    
    def post(self, request, *args, **kwargs):
        task_form = TaskModelForm(request.POST)
        document_form = TaskDocumentForm(request.POST)

        if task_form.is_valid() and document_form.is_valid():
            # assigned_to = task_form.cleaned_data['assigned_to']
            # group_chat = task_form.cleaned_data['create_group_chat']
            manager = Employee.objects.get(user=self.request.user)
            task = task_form.save(commit=False)
            task.created_by = manager
            task.company = manager.company
            task.create_group_chat = task_form.cleaned_data['create_group_chat']
            task.save()
            task.assigned_to.set(task_form.cleaned_data['assigned_to'])
            document = document_form.save(commit=False)
            document.task = task
            document.save()
            return redirect(reverse('leads:task_list'))
        return render(request, self.template_name, {"task_form":task_form, 'document_form':document_form})
        

def htmx_check_create_group_chat(request):
    assigned_ids = request.POST.getlist('assigned_to')
    if len(assigned_ids) >= 2:
        html = render_to_string('leads/partials/group_chat_toggle.html')
    else:
        html = ''  # Return empty so the checkbox disappears
    return HttpResponse(html)

class TaskUpdateView(CustomLoginRequiredMixin, UpdateView):
    template_name = 'leads/update.html'
    form_class = TaskModelForm

    def get_queryset(self):
        user = self.request.user
        return Task.objects.filter(company=user.company)

    def get_success_url(self):
        return reverse("leads:task_list")
    
class TaskDeleteView(CustomLoginRequiredMixin, DeleteView):
    template_name = 'leads/delete.html'
    
    def get_queryset(self):
        user = self.request.user
        return Task.objects.filter(profile=user.userprofile)

    def get_success_url(self):
        return reverse("leads:task_list")
    
def task_create(request):
    if request.method == 'POST':
        form = TaskModelForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("leads:task_list")
    form = TaskModelForm()
    return render(request, 'leads/create.html', {'form':form})

def task_update(request, pk):
    task = Task.objects.get(id=pk)
    form = TaskModelForm(instance=task)
    if request.method == 'POST':
        form = TaskModelForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect("leads:task_list")
    return render(request, 'leads/update.html', {'task': task, 'form':form})

def task_delete(request, pk):
    task = Task.objects.get(id=pk)
    task.delete()
    redirect("leads:task_list")

class SignupView(generic.CreateView):
    template_name = 'registration/signup.html'
    form_class = CustomUserCreationForm

    def get_success_url(self):
        return reverse('create_company')

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response
    
class CompanyCreationView(LoginRequiredMixin, CreateView):
    form_class = CompanyModelForm
    template_name = 'registration/create_company.html'
    login_url = 'login'

    def get_success_url(self):
        return reverse('leads:task_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['employee'] = Employee.objects.get(user=self.request.user)
        except Employee.DoesNotExist:
            context['employee'] = None
        return context
    
    def form_valid(self, form):
        company = form.save(commit=False)
        company.user = self.request.user
        company.save()
        Employee.objects.create(role='manager', company=company, user = self.request.user)
        return redirect(self.get_success_url())
        
def task_per_employee(request):
    today = now()
    start_of_week = today - timedelta(days=today.weekday())  
    end_of_week = start_of_week + timedelta(days=6)          

    employee = Employee.objects.get(user=request.user)
    if employee.role == 'manager':
        employees = Employee.objects.filter(company=employee.company).annotate(completed_task=Count('assigned_task', filter=Q(assigned_task__status='completed', assigned_task__completed_at__date__range=(start_of_week.date(), end_of_week.date()))))
        record = {}
        for employee in employees:
            record[employee.user.username] = employee.completed_task
        return JsonResponse(record)

def task_approval(request, id):
    task = get_object_or_404(Task, id=id)
    task_name = task.title
    employee = Employee.objects.get(user=request.user)
    if task.requires_approval and employee.role != 'manager':
        manager = task.created_by
        if task.status != 'pending_approval':
            send_mail(
                    subject='Tasks pending approval',
                    message=f'This task({task_name}) is pending approval, login to approve it',
                    from_email=str(manager.company.email),
                    recipient_list=[manager.user.email]
                )
            task.status = 'pending_approval'
            task.save()
        return redirect('leads:task_list')
    else:
        task.status = 'completed'
        task.completed_at = timezone.now()
        task.save()
        return redirect('leads:task_list')
    


# class AssignDependencyView(CustomLoginRequiredMixin, generic.View):
#     template_name = 'leads/task_dependency.html'

#     def get(self, request, *args, **kwargs):
#         tasks = Task.objects.filter(company=request.user.employee.company)
#         task_dependencies = TaskDependency.objects.filter(company=request.user.employee.company)
#         dependency_form = AssignTaskDependencyForm(user=request.user)
#         return render(request, self.template_name, {'dependency_form':dependency_form, 'dependencies':task_dependencies, 'tasks':tasks})
    
#     def post(self, request, *args, **kwargs):
#         task_dependencies = TaskDependency.objects.filter(company=request.user.employee.company)
#         tasks = Task.objects.filter(company=request.user.employee.company)
#         dependency_form = AssignTaskDependencyForm(request.POST, user=request.user)
#         if dependency_form.is_valid():
#             cd = dependency_form.cleaned_data
#             from_task = cd['from_task']
#             to_task = cd['to_task']
#             dependency_type = cd['dependency_type']
#             TaskDependency.objects.create(from_task=from_task, to_task=to_task, dependency=dependency_type)
            
#         return render(self.request, self.template_name, {'dependency_form':dependency_form, 'dependencies':task_dependencies, 'tasks':tasks})



# class DependencyUpdate(CustomLoginRequiredMixin, generic.UpdateView):
#     form_class = AssignTaskDependencyForm
#     model = TaskDependency
#     template_name = 'leads/task_dependency.html'

#     def get_success_url(self):
#         return reverse("leads:assign_dependency")
    
#     def get_queryset(self):
#         return TaskDependency.objects.filter(company=self.request.user.employee.company)

#     def get_form_kwargs(self):
#         kwargs = super().get_form_kwargs()
#         kwargs['user'] = self.request.user
#         return kwargs

class DependencyDeleteView(CustomLoginRequiredMixin, DeleteView):
    model = TaskDependency

    def form_valid(self, form):
        if self.request.headers.get('HX-Request'):
            self.object.delete()
            return HttpResponse('') 
        
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("leads:manage_dependencies")
    
    def get_queryset(self):
        return TaskDependency.objects.filter(company=self.request.user.employee.company)


class ManageDependency(CustomLoginRequiredMixin, generic.View):
    template_name = 'leads/manage_dependencies.html'
    def get(self, request, *args, **kwargs):
        tasks = Task.objects.filter(company=request.user.employee.company)
        task_dependencies = TaskDependency.objects.filter(company=request.user.employee.company)
        dependency_form = AssignTaskDependencyForm(user=request.user)

        context = {
            'dependency_form': dependency_form,
            'dependencies': task_dependencies,
            'tasks': tasks,
        }
        
        return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        form = AssignTaskDependencyForm(request.POST, user=request.user)
        if form.is_valid():
            cd = form.cleaned_data
            dependency = TaskDependency.objects.create(from_task=cd['from_task'],to_task=cd['to_task'],dependency_type=cd['dependency_type'],company=request.user.employee.company)

            if request.headers.get('HX-Request'):
                return render(request, 'leads/partials/dependency_readonly.html', {
                    'dependency': dependency,
                    'user': request.user
                })
        tasks = Task.objects.filter(company=request.user.employee.company)
        task_dependencies = TaskDependency.objects.filter(company=request.user.employee.company)
        context = {
            'dependency_form': form,
            'dependencies': task_dependencies,
            'tasks': tasks,
        }
        
        return render(request, self.template_name, context)

class DependencyEditView(CustomLoginRequiredMixin, generic.View):
    def get(self, request, pk):
        if request.GET.get('cancel'):
            dependency = get_object_or_404(TaskDependency, id=pk, company=request.user.employee.company)
            return render(request, 'leads/partials/dependency_readonly.html', {'dependency': dependency,'user': request.user})
        
        dependency = get_object_or_404(TaskDependency, id=pk)
        dependency_form = AssignTaskDependencyForm(user=request.user, 
                                         initial={'from_task':dependency.from_task,
                                                'to_task':dependency.to_task,
                                                 'dependency_type':dependency.dependency_type})
        return render(request, 'leads/partials/dependency_edit.html', {
            'dependency': dependency,
            'form': dependency_form,
            'user': request.user
        })
    
    def post(self, request, pk):    
        dependency = get_object_or_404(
            TaskDependency, 
            id=pk, 
            company=request.user.employee.company
        )
        
        form = AssignTaskDependencyForm(request.POST, user=request.user)
        
        if form.is_valid():
            cd = form.cleaned_data
            dependency.from_task = cd['from_task']
            dependency.to_task = cd['to_task']
            dependency.dependency_type = cd['dependency_type']
            dependency.save()
            
            
            return render(request, 'leads/partials/dependency_readonly.html', {
                'dependency': dependency,
                'user': request.user
            })
        
        return render(request, 'leads/partials/dependency_edit.html', {
            'dependency': dependency,
            'form': form,
            'user': request.user
        })

class AgentAssignView(CustomLoginRequiredMixin, generic.View):
    def get(self, request, id):
        task = Task.objects.get(id=id)
        form = AgentAssignForm(user=request.user, task=task)
        return render(request, 'leads/assign_agent.html', {'form':form})
    
    def post(self, request, id):
        task = Task.objects.get(id=id)
        form = AgentAssignForm(request.POST, user=request.user, task=task)

        if form.is_valid():
            agents = form.cleaned_data['assigned_to']
            task.create_group_chat = form.cleaned_data['create_group_chat']
            task.save()
            task.assigned_to.set(agents)
            return redirect('leads:task_list')
        
        return render(request, 'leads/assign_agent.html', {'form':form})
    
