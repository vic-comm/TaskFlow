from django.test import TestCase
import pytest
from django.core import mail
from django.utils.timezone import now, timedelta
from .models import TaskDependency
from django.core.exceptions import ValidationError
from automation.models import TemplateDependency
# Create your tests here.

@pytest.mark.django_db
def test_no_dependencies_still_pending(task_factory):
    task = task_factory()
    # evaluate_dependency_status(task)
    task.refresh_from_db()
    assert task.status == 'pending'

@pytest.mark.django_db
@pytest.mark.parametrize(
    "dep_type, from_status, expected", [
        ("finish_to_start", "completed", "pending"),
        ("finish_to_start", "in_progress", "suspended"),
        ("start_to_start", "in_progress", "pending"),
        ("start_to_start", "pending", "suspended"),
        ("finish_to_finish", "completed", "pending"),
        ("finish_to_finish", "in_progress", "suspended"),
        ("start_to_finish", "in_progress", "pending"),
        ("start_to_finish", "pending", "suspended"),
    ]
)

@pytest.mark.django_db
def test_dependency_types(task_factory,company_factory, dep_type, from_status, expected):
    from_task = task_factory(status=from_status)
    to_task = task_factory()
    company = company_factory()
    TaskDependency.objects.create(from_task=from_task, to_task=to_task, dependency_type=dep_type, company=company)

    to_task.refresh_from_db()

    assert to_task.status == expected

@pytest.mark.django_db
def test_multidependencies_all_must_satisfied(task_factory, company_factory):
    from_task1 = task_factory(status="completed")
    from_task2 = task_factory(status="in_progress")
    to_task = task_factory(status="pending")
    company = company_factory()

    TaskDependency.objects.create(from_task=from_task1, to_task=to_task, dependency_type="finish_to_start", company=company)
    TaskDependency.objects.create(from_task=from_task2, to_task=to_task, dependency_type="finish_to_start", company=company)

    to_task.refresh_from_db()

    assert to_task.status == "suspended"

@pytest.mark.django_db
def test_task_unblocks_when_all_dependencies_satisfied(task_factory, company_factory):
    from_task1 = task_factory(status="completed")
    from_task2 = task_factory(status="completed")
    to_task = task_factory(status="suspended")
    company = company_factory()

    TaskDependency.objects.create(from_task=from_task1, to_task=to_task, dependency_type="finish_to_start", company=company)
    TaskDependency.objects.create(from_task=from_task2, to_task=to_task, dependency_type="finish_to_start", company=company)

    to_task.refresh_from_db()

    assert to_task.status == "pending"

@pytest.mark.django_db
def test_removing_dependencies(task_factory, company_factory):
    from_task1 = task_factory(status="pending")
    to_task = task_factory(status="pending")
    company = company_factory()

    TaskDependency.objects.create(from_task=from_task1, to_task=to_task, dependency_type='finish_to_start', company=company)
    to_task.refresh_from_db()
    assert to_task.status == 'suspended'

    from_task1.delete()
    to_task.refresh_from_db()
    assert to_task.status == 'pending'


@pytest.mark.parametrize(
    "dep_type, from_status, start_offset, duration", [
        ("finish_to_start", "completed", 0, 3),
        ("finish_to_start", "in_progress", 0, 3),
        ("start_to_start", "in_progress", 1, 5),
        ("start_to_start", "pending", 1, 5),
        ("finish_to_finish", "completed", 2, 4),
        ("finish_to_finish", "in_progress", -2, 4),
        ("start_to_finish", "in_progress", 2, 6),
        ("start_to_finish", "pending", 2, 6),
    ]
)
@pytest.mark.django_db
def test_dependency_date(task_factory, company_factory, dep_type, from_status, start_offset, duration):
    base = now()
    company = company_factory()
    from_task = task_factory(status=from_status, start_date=base, end_date=base+timedelta(days=2))
    to_task = task_factory(start_date=base + timedelta(days=start_offset), end_date=base+timedelta(days=start_offset+duration))
    TaskDependency.objects.create(from_task=from_task, to_task=to_task, dependency_type=dep_type, company=company)

    duration = timedelta(days=duration)
    to_task.refresh_from_db()
    assert to_task.end_date - to_task.start_date == duration

    if dep_type == "finish_to_start" and from_status == "completed":
        assert to_task.status == "pending"
        assert to_task.start_date >= from_task.end_date

    elif dep_type == "start_to_start" and from_status in ["in_progress", "started", "completed"]:
        assert to_task.status == "pending"
        assert to_task.start_date >= from_task.start_date

    elif dep_type == "finish_to_finish" and from_status == "completed":
        assert to_task.status == "pending"
        assert to_task.end_date >= from_task.end_date

    elif dep_type == "start_to_finish" and from_status in ["in_progress", "started", "completed"]:
        assert to_task.status == "pending"
        assert to_task.end_date >= from_task.start_date

    else:
        assert to_task.status == "suspended"

@pytest.mark.django_db
def test_circular_dependency(task_factory, company_factory):
    company = company_factory()
    task1 = task_factory(company=company)
    task2 = task_factory(company=company)
    task3 = task_factory(company=company)

    TaskDependency.objects.create(from_task=task1, to_task=task2, dependency_type='finish_to_start', company=company)
    TaskDependency.objects.create(from_task=task2, to_task=task3, dependency_type='finish_to_start', company=company)
    with pytest.raises(ValidationError):
        TaskDependency.objects.create(from_task=task3, to_task=task1, dependency_type='finish_to_start', company=company)
        
@pytest.mark.django_db
def test_email_sent(task_factory, employee_factory):
    employee1 = employee_factory(role='manager')
    employee2 = employee_factory()
    employee3 = employee_factory()

    task = task_factory()
    task.assigned_to.set([employee1, employee2, employee3])
    assert len(mail.outbox) == 1

    recipients = mail.outbox[0].to
    assert set(recipients) == set([employee1.user.email, employee2.user.email, employee3.user.email])
    
@pytest.mark.django_db
def test_chatgroup_creation(task_factory, employee_factory):
    employee1 = employee_factory(role='manager')
    employee2 = employee_factory()
    employee3 = employee_factory()

    task = task_factory(create_group_chat=True)
    task.assigned_to.set([employee1, employee2, employee3])
    task.save()
    task.refresh_from_db()

    assert task.group_chat.members.count() == 3

    task.assigned_to.remove(employee2)
    task.refresh_from_db()

    assert task.group_chat.members.count() == 2
    assert employee2.user not in list(task.group_chat.members.all())

@pytest.mark.django_db
def test_workflow_automation(work_flow_factory, template_factory, company_factory):
    company = company_factory()
    workflow = work_flow_factory(company=company)
    
    temp1 = template_factory(template=workflow)
    temp2 = template_factory(template=workflow)
    temp3 = template_factory(template=workflow)

    TemplateDependency.objects.create(from_task = temp1, to_task=temp2, dependency_type='finish_to_start')
    TemplateDependency.objects.create(from_task = temp2, to_task=temp3, dependency_type='finish_to_start')

    with pytest.raises(ValidationError):
        TemplateDependency.objects.create(from_task = temp3, to_task=temp1, dependency_type='finish_to_start')
    with pytest.raises(ValidationError):
        TemplateDependency.objects.create(from_task = temp3, to_task=temp3, dependency_type='finish_to_start')
    


    



    








