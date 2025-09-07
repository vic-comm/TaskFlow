from django.contrib import admin
from .models import User,  Task, Employee, Company, TaskDependency
# Register your models here.
admin.site.register(User)
admin.site.register(Company)
admin.site.register(Task)
admin.site.register(TaskDependency)
admin.site.register(Employee)