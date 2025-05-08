from django import forms
from leads.models import Employee
from django.contrib.auth import get_user_model
User = get_user_model()
class EmployeeCreationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'username']