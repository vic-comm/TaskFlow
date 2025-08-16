from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(TemplateTask)
admin.site.register(TemplateDependency)
admin.site.register(WorkFlowTemplate)