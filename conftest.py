import pytest
from pytest_factoryboy import register
from leads.factories import UserFactory, EmployeeFactory, CompanyFactory, TaskDependencyFactory, TaskFactory, TemplateFactory, WorkFlowFactory

register(UserFactory)
register(EmployeeFactory)
register(CompanyFactory)
register(TaskDependencyFactory)
register(TaskFactory)
register(TemplateFactory)
register(WorkFlowFactory)
