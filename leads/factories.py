import factory
from leads import models 
from faker import Faker
from django.utils.timezone import now, timedelta
from automation.models import WorkFlowTemplate, TemplateTask
fake = Faker()
class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.User

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda o: f"{o.username}@email.com")
    password = factory.PostGenerationMethodCall('set_password', 'password13')

class CompanyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Company
    
    user = factory.SubFactory(UserFactory)
    name = factory.Faker('name')

class EmployeeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Employee

    user = factory.SubFactory(UserFactory)
    company = factory.SubFactory(CompanyFactory)
    role = "employee"

class TaskFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Task
    company = factory.SubFactory(CompanyFactory)
    created_by = factory.SubFactory(EmployeeFactory)
    title = factory.Faker('sentence', nb_words=4)
    status = 'pending'
    start_date = now()
    end_date = now() + timedelta(days=1)

class TaskDependencyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.TaskDependency
    
    from_task = factory.SubFactory(TaskFactory)
    to_task = factory.SubFactory(TaskFactory)
    company = factory.SubFactory(CompanyFactory)


class WorkFlowFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = WorkFlowTemplate

    name = factory.Faker('name')
    description = factory.Faker('sentence', nb_words=4)
    company = factory.SubFactory(CompanyFactory)
    created_by = factory.SubFactory(EmployeeFactory, role='manager')

class TemplateFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TemplateTask
    
    template = factory.SubFactory(WorkFlowFactory)
    title = factory.Faker('sentence', nb_words=4)
    