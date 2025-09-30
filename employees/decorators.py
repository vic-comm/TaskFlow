from functools import wraps
from django.shortcuts import get_object_or_404, redirect
from leads.models import Employee

def manager_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        employee = get_object_or_404(Employee, user=request.user)
        if not (request.user.is_authenticated and employee.role == 'manager'):
            return redirect('leads:task_list')
        return view_func(request, *args, **kwargs)
    return _wrapped_view