from django.shortcuts import render, reverse
from .forms import EmployeeCreationForm
from django.core.mail import send_mail
from django.views import generic
import random
from django.contrib.auth.mixins import LoginRequiredMixin
from .mixins import CustomLoginRequiredMixin
from leads.models import Employee
# Create your views here.

class EmployeeListView(CustomLoginRequiredMixin, generic.ListView):
    template_name = 'employees/list.html'

    def get_queryset(self):
        # profile = self.request.user.userprofile
        # return Employee.objects.filter(profile=profile)
        return Employee.objects.all()
class EmployeeCreateView(CustomLoginRequiredMixin, generic.CreateView):
    template_name = 'employees/create.html'
    form_class = EmployeeCreationForm

    def get_success_url(self):
        return reverse('employees:employee_list')
    
    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_organisor = False
        user.is_agent = True
        user.set_password(f"{random.randint(0, 100000)}")
        user.save()
        Employee.objects.create(user=user, profile=self.request.user.userprofile)
        send_mail(subject='Congrats You have joined Damisa Gurus as an employee', message='Login to view assigned task', from_email='obiezuechidera@gmail.com', recipient_list=[user.email])
        return super(EmployeeCreateView, self).form_valid(form)


class EmployeeDetailView(CustomLoginRequiredMixin, generic.DetailView):
    template_name = 'employees/detail.html'
    context_object_name = 'employee'
    
    def get_queryset(self):
        return Employee.objects.all()
    
class EmployeeUpdateView(CustomLoginRequiredMixin, generic.UpdateView):
    template_name = 'employees/update.html'
    form_class = EmployeeCreationForm
    context_object_name = 'employee'

    def get_success_url(self):
        return reverse('employees:employee_list')
    
    def get_queryset(self):
        return Employee.objects.all()
    

class EmployeeDeleteView(CustomLoginRequiredMixin, generic.DeleteView):
    template_name = 'employees/delete.html'
    
    def get_queryset(self):
        return Employee.objects.all()
    
    def get_success_url(self):
        return reverse('employees:employee_list')
    