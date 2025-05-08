from django.urls import path
from . import views
import django.contrib.auth.views as auth_views

app_name = 'leads'
urlpatterns = [
     # path('', views.task_list, name='task_list'),
     path('', views.TaskListView.as_view(), name='task_list'),
     path('task_detail/<int:pk>/', views.TaskDetailView.as_view(), name='task_detail'),
     path('task_create/', views.TaskCreateView.as_view(), name='task_create'),
     path('task_update/<int:pk>/', views.TaskUpdateView.as_view(), name='task_update'),
     path('task_category_update/<int:pk>/', views.TaskCategoryUpdateView.as_view(), name='task_category_update'),
     path('task_delete/<int:pk>/', views.TaskDeleteView.as_view(), name='task_delete'),
     path('task_assign/<int:pk>/', views.AgentAssignView.as_view(), name='assign_agent'),
     path('categories/', views.CategoryListView.as_view(), name='category_list'),
     path('categories/<int:pk>/', views.CategoryDetailView.as_view(), name='category_detail'),
]
