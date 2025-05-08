from django.contrib import admin
from .models import User,  Task, Employee, UserProfile, Category
# Register your models here.
admin.site.register(User)
admin.site.register(Category)
admin.site.register(UserProfile)
admin.site.register(Task)
admin.site.register(Employee)