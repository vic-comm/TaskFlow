import factory
from leads import models 
from faker import Faker
from django.utils.timezone import now, timedelta
from leads import models
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

