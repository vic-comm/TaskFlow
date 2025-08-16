from django.urls import path
from . import views
import django.contrib.auth.views as auth_views

app_name = 'leads'
urlpatterns = [
     path('', views.TaskListView.as_view(), name='task_list'),
     path('task_detail/<int:pk>/', views.TaskDetailView.as_view(), name='task_detail'),
     path('task_create/', views.TaskCreateView.as_view(), name='task_create'),
     path('task_update/<int:pk>/', views.TaskUpdateView.as_view(), name='task_update'),
     path('task_delete/<int:pk>/', views.TaskDeleteView.as_view(), name='task_delete'),
     # path('task_assign/<int:pk>/', views.AgentAssignView.as_view(), name='assign_agent'),
     path('htmx-check/', views.htmx_check_create_group_chat, name='htmx_check'),
     path('task_approval/<int:pk>/', views.task_approval, name='task_approval'),
     # path('assign_dependency/', views.AssignDependencyView.as_view(), name='assign_dependency'),
     path('dependencies/', views.ManageDependency.as_view(), name='manage_dependencies'),
     path('dependencies/edit/<int:pk>/', views.DependencyEditView.as_view(), name='dependency_edit'),
     path('dependencies/delete/<int:pk>/', views.DependencyDeleteView.as_view(), name='dependency_delete'),

]
