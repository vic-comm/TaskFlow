from django.urls import path
from . import views
app_name = 'employees'

urlpatterns = [
     # path('', views.task_list, name='task_list'),
     path('', views.EmployeeListView.as_view(), name='employee_list'),
     path('employee_detail/<int:pk>/', views.EmployeeDetailView.as_view(), name='employee_detail'),
     path('employee_create/', views.EmployeeCreateView.as_view(), name='create_employee'),
     path('employee_update/<int:pk>/', views.EmployeeUpdateView.as_view(), name='employee_update'),
     path('employee_delete/<int:pk>/', views.EmployeeDeleteView.as_view(), name='employee_delete'),
]
