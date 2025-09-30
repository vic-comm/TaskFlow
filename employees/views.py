from django.shortcuts import render, reverse
from .forms import EmployeeCreationForm
from django.core.mail import send_mail
from django.views import generic
import random
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
from .mixins import CustomLoginRequiredMixin
from leads.models import Employee
from .decorators import manager_required
# Create your views here.

class EmployeeListView(CustomLoginRequiredMixin, generic.ListView):
    template_name = 'employees/list.html'

    def get_queryset(self):
        employee = Employee.objects.get(user=self.request.user)
        return Employee.objects.filter(company=employee.company)
    
class EmployeeCreateView(CustomLoginRequiredMixin, generic.CreateView):
    template_name = 'employees/create.html'
    form_class = EmployeeCreationForm

    def get_success_url(self):
        return reverse('employees:employee_list')
    
    def form_valid(self, form):
        try:
            manager = Employee.objects.get(user=self.request.user)
        except Employee.DoesNotExist:
            form.add_error(None, 'current user has no employee record')
            return self.form_invalid(form)
        
        user = form.save(commit=False)
        cd = form.cleaned_data
        user.set_password(f"{random.randint(0, 100000)}")
        user.save()
        is_manager = cd['manager']
        if is_manager:
            Employee.objects.create(user=user, company=manager.company, role='manager')
        else:
            Employee.objects.create(user=user, company=manager.company, role='employee')
        company_name = manager.company.name
        user_name = cd['username']
        user_email = cd['email']
        company_email = manager.company.email
        send_mail(subject=f'Congrats You have joined {company_name} as an employee', message=f'Login to view assigned task, login with username {user_name} and click forgot password to generate new password', from_email=f'{company_email}', recipient_list=[user_email])
        return HttpResponseRedirect(self.get_success_url())

class EmployeeDetailView(CustomLoginRequiredMixin, generic.DetailView):
    template_name = 'employees/detail.html'
    context_object_name = 'employee'
    
    def get_queryset(self):
        return Employee.objects.all()
    
class EmployeeUpdateView(LoginRequiredMixin, generic.UpdateView):
    template_name = 'employees/update.html'
    form_class = EmployeeCreationForm
    context_object_name = 'employee'

    def get_success_url(self):
        return reverse('employees:employee_list')
    
    def get_queryset(self):
        queryset = Employee.objects.filter(user=self.request.user)
        return queryset
    

class EmployeeDeleteView(CustomLoginRequiredMixin, generic.DeleteView):
    template_name = 'employees/delete.html'
    
    def get_success_url(self):
        return reverse('employees:employee_list')
    