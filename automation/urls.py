from django.urls import path
from automation import views
app_name='workflow'
urlpatterns = [
    path('', views.workflow_list, name='workflow_list'),
    path('create_template/<int:workflow_id>/', views.create_template_task, name='create_template'),
    path('deploy_workflow/<int:workflow_id>/', views.deploy_workflow, name='deploy_workflow'),
    path('assign_dependency/<int:workflow_id>/', views.assign_template_dependency, name='assign_dependency'),
    path('workflow_detail/<int:workflow_id>/', views.workflow_detail, name='workflow_detail'),
    path('workflow/htmx_check/', views.htmx_check_create_group_chat, name='htmx_check'),
    path('workflow/delete_template<int:workflow_id>/<int:task_id>/', views.delete_template, name='delete_template'),
    path('workflow_delete/<int:workflow_id>/', views.delete_workflow, name='delete_workflow'),
]
