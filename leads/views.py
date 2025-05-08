from django.shortcuts import render, redirect, reverse
from .models import Task, Category
from django.core.mail import send_mail
from .forms import TaskModelForm
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import CustomUserCreationForm, AgentAssignForm, TaskUpdateCategoryForm
from django.views import generic
from employees.mixins import CustomLoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
# Create your views here.

def task_detail(request, pk):
    task = Task.objects.get(id=pk)
    return render(request, 'leads/detail.html', {'task':task})

def task_list(request):
    tasks = Task.objects.all()
    return render(request, 'leads/list.html', {'tasks':tasks})

class TaskListView(LoginRequiredMixin, ListView):
    template_name = 'leads/list1.html'
    context_object_name = 'task_list'

    def get_queryset(self):
        user = self.request.user
        if user.is_organisor:
            # queryset = Task.objects.filter(profile=user.userprofile)
            queryset = Task.objects.filter(employee__isnull = False)
        else:
            queryset = Task.objects.filter(profile=user.employee.profile, employee__isnull = False)
            queryset.filter(employee__user=user)
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_organisor:
            queryset = Task.objects.filter(employee__isnull = True)
            context.update({'unassigned': queryset})
        return context

class TaskDetailView(LoginRequiredMixin, DetailView):
    template_name = 'leads/detail.html'
    context_object_name = 'task'

    def get_queryset(self):
        user = self.request.user
        if user.is_organisor:
            # queryset = Task.objects.filter(profile=user.userprofile)
            queryset = Task.objects.all()
        else:
            queryset = Task.objects.filter(profile=user.employee.profile)
            queryset.filter(employee__user=user)
        return queryset

class TaskCreateView(CustomLoginRequiredMixin, CreateView):
    template_name = 'leads/create.html'
    form_class = TaskModelForm

    def get_success_url(self):
        return reverse("leads:task_list")
    
    def form_valid(self, form):
        send_mail(
            subject='You task created',
            message='Login to check it out',
            from_email='obiezuevictor@email.com',
            recipient_list=[str(self.form['employee'].email)]
        )
        return super(TaskCreateView, self).form_valid(form)
    

class TaskUpdateView(CustomLoginRequiredMixin, UpdateView):
    template_name = 'leads/update.html'
    form_class = TaskModelForm

    def get_queryset(self):
        user = self.request.user
        return Task.objects.filter(profile=user.userprofile)

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
        return reverse('leads:task_list')

class AgentAssignView(CustomLoginRequiredMixin, generic.FormView):
    form_class = AgentAssignForm
    template_name = 'leads/assign_agent.html'

    def get_success_url(self):
        return reverse('leads:task_list')
    
    # def get_form_kwargs(self):
    #     return {'request': self.request}

    def form_valid(self, form):
        employee = form.cleaned_data['agent']
        task = Task.objects.get(id=self.kwargs['pk'])
        task.employee = employee
        task.save()
        return super().form_valid(form)
    
class CategoryListView(LoginRequiredMixin, ListView):
    template_name = 'leads/category_list.html'
    context_object_name = 'category_list'

    def get_context_data(self, **kwargs):
        user = self.request.user
        if user.is_organisor:
            # queryset = Task.objects.filter(profile=user.userprofile)
            queryset = Task.objects.all()
        else:
            queryset = Task.objects.filter(profile=user.employee.profile)
        context = super().get_context_data(**kwargs)
        context.update({'unassigned_count':queryset.filter(category__isnull=True).count()})
        return context
    
    def get_queryset(self):
        user = self.request.user
        if user.is_organisor:
            # queryset = Task.objects.filter(profile=user.userprofile)
            queryset = Category.objects.all()
        else:
            queryset = Category.objects.filter(profile=user.employee.profile)
        return queryset
    
    
    
    
class CategoryDetailView(LoginRequiredMixin, generic.DetailView):
    template_name = 'leads/category_detail.html'
    context_object_name = 'category'

    def get_queryset(self):
        user = self.request.user
        if user.is_organisor:
            # queryset = Task.objects.filter(profile=user.userprofile)
            queryset = Category.objects.all()
        else:
            queryset = Category.objects.filter(profile=user.employee.profile)
        return queryset
    
    def get_context_data(self, **kwargs):
        queryset = self.get_object().tasks.all()
        context = super().get_context_data(**kwargs)
        context.update({'tasks':queryset})
        return context

class TaskCategoryUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'leads/task_category_update.html'
    form_class = TaskUpdateCategoryForm
    # context_object_name = 'task'

    def get_queryset(self):
        user = self.request.user
        if user.is_organisor:
            # queryset = Task.objects.filter(profile=user.userprofile)
            queryset = Task.objects.all()
        else:
            queryset = Task.objects.filter(profile=user.employee.profile)
            queryset.filter(employee__user=user)
        return queryset
    
    def get_success_url(self):
        return redirect('leads:task_detail', kwargs={'pk':self.get_object().id})