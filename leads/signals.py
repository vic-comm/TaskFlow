from django.db.models.signals import post_save, post_delete, m2m_changed
from .models import Task, TaskDependency, Employee
from django.dispatch import receiver
from django.core.mail import send_mail
from chat.models import ChatGroup

def evaluate_dependency_status(task):
    """
    Evaluates all dependencies and either blocks or unblocks the task.
    """
    from leads.models import TaskDependency

    dependencies = TaskDependency.objects.filter(to_task=task)
    still_blocked = False

    for dep in dependencies:
        from_task_status = dep.from_task.status
        dep_type = dep.dependency_type

        if dep_type == 'finish_to_start' and from_task_status != 'completed':
            still_blocked = True
        elif dep_type == 'start_to_start' and from_task_status not in ['in_progress', 'started']:
            still_blocked = True
        elif dep_type == 'finish_to_finish' and from_task_status != 'completed':
            still_blocked = True
        elif dep_type == 'start_to_finish' and from_task_status not in ['in_progress', 'started']:
            still_blocked = True

        if still_blocked:
            break

    if still_blocked and task.status != 'suspended':
        task.status = 'suspended'
        task.save(update_fields=['status'])

    elif not still_blocked and task.status == 'suspended':
        task.status = 'pending'
        task.save(update_fields=['status'])

@receiver(post_save, sender=Task)
def check_unblock_dependent_task(sender, instance, **kwargs):
    updated_task = instance
    updated_status = instance.status

    dependencies = TaskDependency.objects.filter(from_task=updated_task)
    for dep in dependencies:
        dependent_task = dep.to_task
        dependency_type = dep.dependency_type

        is_satisfied = False
        if dependency_type == 'finish_to_start' and updated_status == 'completed':
            is_satisfied = True
        elif dependency_type == 'start_to_start' and updated_status in ['completed', 'pending']:
            is_satisfied = True
        elif dependency_type == 'finish_to_finish' and updated_status == 'completed':
            is_satisfied = True
        elif dependency_type == 'start_to_finish' and updated_task.status in ['completed', 'pending']:
            is_satisfied = True

        if is_satisfied:
            all_deps = TaskDependency.objects.filter(to_task=dependent_task)

            still_blocked = False
            for other_dep in all_deps:
                from_task_status = other_dep.from_task.status
                dep_type = other_dep.dependency_type

                
                if dep_type == 'finish_to_start' and from_task_status != 'completed':
                    still_blocked = True
                elif dep_type == 'start_to_start' and from_task_status not in ['completed', 'pending']:
                    still_blocked = True
                elif dep_type == 'finish_to_finish' and from_task_status != 'completed':
                    still_blocked = True
                elif dep_type == 'start_to_finish' and from_task_status not in ['completed', 'pending']:
                    still_blocked = True

                if still_blocked:
                    break

                # Unblock the task if all dependencies are satisfied
                if not still_blocked:
                    if dependent_task.is_blocked():
                        dependent_task.status = 'pending'
                        dependent_task.save(update_fields=['status'])
                       

@receiver(post_save, sender=TaskDependency)
def post_dependency_update(sender, instance, **kwargs):
    to_task = instance.to_task
    evaluate_dependency_status(to_task)

@receiver(post_delete, sender=TaskDependency)
def post_delete_update(sender, instance, **kwargs):
    evaluate_dependency_status(instance.to_task)

@receiver(m2m_changed, sender=Task.assigned_to.through)
def create_chat_send_email(sender, instance, action, pk_set, **kwargs):
    if action == 'post_add':
        task = instance
        manager = task.created_by
        assigned_to = task.assigned_to.all()
        new_employees = Employee.objects.filter(pk__in=pk_set)
        send_mail(subject='You have been assigned a task',
                message='Login to check it out',
                from_email=str(manager.company.email) if manager.company.email else str(manager.user.email),
                recipient_list=[employee.user.email for employee in new_employees])
        
        if task.create_group_chat:
            if not hasattr(task, 'group_chat'):
                task_group = ChatGroup.objects.create(admin=task.created_by.user, groupchat_name=task.title, task=task)
                task_group.members.set([emp.user for emp in assigned_to])
                task.group_chat = task_group
                task.save()
            else:
                task.group_chat.members.add(*[emp.user for emp in new_employees])
    elif action == 'post_remove':
        task = instance
        assigned_to = task.assigned_to.all()
        removed_employees = Employee.objects.filter(pk__in=pk_set)
        if hasattr(task, 'group_chat'):
            task.group_chat.members.remove(*[emp.user for emp in removed_employees])

@receiver(post_delete, sender=Task)
def handle_delete(sender, instance, **kwargs):
    if instance.group_chat_id: 
        try:
            instance.group_chat.delete()
        except ChatGroup.DoesNotExist:
            pass

    if instance.workflow:
        workflow = instance.workflow
        remaining_tasks = workflow.workflow_tasks.all()
        if not remaining_tasks.exists():
            workflow.is_active = False

@receiver(post_save, sender=Task)
def check_workflow(sender, instance, **kwargs):
    if instance.workflow:
        workflow = instance.workflow
        tasks = workflow.workflow_tasks.all()
        for task in tasks:
            if task.status != 'completed':
                return
        workflow.is_active = False
        workflow.save()