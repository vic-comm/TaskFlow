from django.db.models.signals import post_save, post_delete, m2m_changed
from .models import Task, TaskDependency, Employee
from django.dispatch import receiver
from django.db import transaction
from django.core.mail import send_mail
from chat.models import ChatGroup
from django.utils.timezone import now, timedelta
def evaluate_dependency_status(task):
    dependencies = TaskDependency.objects.filter(to_task=task)
    still_blocked = False

    for dep in dependencies:
        from_task = dep.from_task
        to_task = dep.to_task
        dep_type = dep.dependency_type

        duration = (to_task.end_date - to_task.start_date) if to_task.start_date and to_task.end_date else timedelta(days=1)

        if dep_type == 'finish_to_start':
            # print(f"Before update: to_task.start_date={to_task.start_date}, from_task.end_date={from_task.end_date}")
            to_task.start_date = max(to_task.start_date or from_task.end_date, from_task.end_date)
            to_task.end_date = to_task.start_date + duration
            # print(f"After update: to_task.start_date={to_task.start_date}")
            if from_task.status != 'completed':
                still_blocked = True

        elif dep_type == 'start_to_start':
            to_task.start_date = max(to_task.start_date or from_task.start_date, from_task.start_date)
            to_task.end_date = to_task.start_date + duration
            if from_task.status not in ['in_progress', 'started', 'completed']:
                still_blocked = True

        elif dep_type == 'finish_to_finish':
            to_task.end_date = max(to_task.end_date or from_task.end_date, from_task.end_date)
            to_task.start_date = to_task.end_date - duration
            if from_task.status != 'completed':
                still_blocked = True

        elif dep_type == 'start_to_finish':
            to_task.end_date = max(to_task.end_date or from_task.start_date, from_task.start_date)
            to_task.start_date = to_task.end_date - duration
            if from_task.status not in ['in_progress', 'started', 'completed']:
                still_blocked = True
                

        if still_blocked:
            break

    
    if still_blocked and task.status != 'suspended':
        task.status = 'suspended'
    elif not still_blocked:
        if task.status == 'suspended':
            task.status = 'pending'
    task.save(update_fields=['status', 'start_date', 'end_date'])

@receiver(post_save, sender=Task)
def check_unblock_dependent_task(sender, instance, **kwargs):
    updated_task = instance
    updated_status = instance.status

    dependencies = TaskDependency.objects.filter(from_task=updated_task)
    for dep in dependencies:
        dependent_task = dep.to_task
        dependency_type = dep.dependency_type

        # check if this dependency condition is satisfied
        is_satisfied = False
        if dependency_type == 'finish_to_start' and updated_status == 'completed':
            is_satisfied = True
        elif dependency_type == 'start_to_start' and updated_status in ['completed', 'pending', 'in_progress']:
            is_satisfied = True
        elif dependency_type == 'finish_to_finish' and updated_status == 'completed':
            is_satisfied = True
        elif dependency_type == 'start_to_finish' and updated_status in ['completed', 'pending', 'in_progress']:
            is_satisfied = True

        if is_satisfied:
            all_deps = TaskDependency.objects.filter(to_task=dependent_task)

            still_blocked = False
            for other_dep in all_deps:
                from_task_status = other_dep.from_task.status
                dep_type = other_dep.dependency_type

                if dep_type == 'finish_to_start' and from_task_status != 'completed':
                    still_blocked = True
                elif dep_type == 'start_to_start' and from_task_status not in ['completed', 'pending', 'in_progress']:
                    still_blocked = True
                elif dep_type == 'finish_to_finish' and from_task_status != 'completed':
                    still_blocked = True
                elif dep_type == 'start_to_finish' and from_task_status not in ['completed', 'pending', 'in_progress']:
                    still_blocked = True

                if still_blocked:
                    break

           
            if not still_blocked:
               
                duration = dependent_task.end_date - dependent_task.start_date if dependent_task.start_date and dependent_task.end_date else timedelta(days=1)
                from_task = updated_task

                if dependency_type == 'finish_to_start':
                    dependent_task.start_date = max(dependent_task.start_date or from_task.end_date, from_task.end_date)
                    dependent_task.end_date = dependent_task.start_date + duration

                elif dependency_type == 'start_to_start':
                    dependent_task.start_date = max(dependent_task.start_date or from_task.start_date, from_task.start_date)
                    dependent_task.end_date = dependent_task.start_date + duration

                elif dependency_type == 'finish_to_finish':
                    dependent_task.end_date = max(dependent_task.end_date or from_task.end_date, from_task.end_date)
                    dependent_task.start_date = dependent_task.end_date - duration

                elif dependency_type == 'start_to_finish':
                    dependent_task.end_date = max(dependent_task.end_date or from_task.start_date, from_task.start_date)
                    dependent_task.start_date = dependent_task.end_date - duration
                
                dependent_task.status = 'pending'
                dependent_task.save() 

    
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
        try:
            with transaction.atomic():
                if task.create_group_chat:
                    if not hasattr(task, 'group_chat'):
                        task_group = ChatGroup.objects.create(admin=task.created_by.user, groupchat_name=f"{task.title}-{task.id}", task=task)
                        task_group.members.set([emp.user for emp in assigned_to] + [manager.user])
                        task.group_chat = task_group
                        task.save()
                    else:
                        task.group_chat.members.add(*[emp.user for emp in new_employees])
            send_mail(subject='You have been assigned a task',
                message='Login to check it out',
                from_email=str(manager.company.email) if manager.company.email else str(manager.user.email),
                recipient_list=[employee.user.email for employee in new_employees])
            
        except Exception as e:
            print(f"Error in task assignment signal: {e}")
            raise

    elif action == 'post_remove':
        task = instance
        removed_employees = Employee.objects.filter(pk__in=pk_set)
        if hasattr(task, 'group_chat'):
            with transaction.atomic():
                task.group_chat.members.remove(*[emp.user for emp in removed_employees])

@receiver(post_save, sender=Task)
def check_workflow(sender, instance, **kwargs):
    workflow = instance.workflow_instance
    if not workflow:
        return
    
    all_completed = not workflow.tasks.exclude(status='completed').exists()

    if all_completed and workflow.status != 'completed':
        workflow.status = "completed"
        workflow.completed_at = now()
        workflow.save(update_fields=["status", "completed_at"])

@receiver(post_delete, sender=Task)
def handle_delete(sender, instance, **kwargs):
    if hasattr(instance, 'group_chat'): 
        try:
            instance.group_chat.delete()
        except ChatGroup.DoesNotExist:
            pass

    
    if instance.workflow_instance:
        workflow = instance.workflow_instance
        all_completed = not workflow.tasks.exclude(status='completed').exists()
        
        if all_completed and workflow.status != 'completed':
            workflow.status = "completed"
            workflow.completed_at = now()
            workflow.save(update_fields=["status", "completed_at"])

    dependencies = TaskDependency.objects.filter(from_task=instance)
    for dep in dependencies:
        dep_type = dep.dependency_type
        to_task = dep.to_task
        from_task = instance
        duration = to_task.end_date - to_task.start_date
        if dep_type == 'finish_to_start':
            to_task.start_date = max(to_task.start_date or from_task.end_date, from_task.end_date)
            to_task.end_date = to_task.start_date + duration
            to_task.status = 'pending'

        elif dep_type == 'start_to_start':
            to_task.start_date = max(to_task.start_date or from_task.start_date, from_task.start_date)
            to_task.end_date = to_task.start_date + duration
            to_task.status = 'pending'

        elif dep_type == 'finish_to_finish':
            to_task.end_date = max(to_task.end_date or from_task.end_date, from_task.end_date)
            to_task.start_date = to_task.end_date - duration
            to_task.status = 'pending'

        elif dep_type == 'start_to_finish':
            to_task.end_date = max(to_task.end_date or from_task.start_date, from_task.start_date)
            to_task.start_date = to_task.end_date - duration
            to_task.status = 'pending'

        to_task.save()
