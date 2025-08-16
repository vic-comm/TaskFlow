from django.contrib.auth.mixins import AccessMixin
from django.shortcuts import redirect, get_object_or_404
from leads.models import Employee

class CustomLoginRequiredMixin(AccessMixin):
    """Verify that the current user is authenticated."""

    def dispatch(self, request, *args, **kwargs):
        employee = get_object_or_404(Employee, user=request.user)
        if not (request.user.is_authenticated and employee.role == 'manager'):
            return redirect('leads:task_list')
        return super().dispatch(request, *args, **kwargs)