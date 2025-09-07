from leads.models import Task, TaskDependency
from datetime import timedelta
from collections import defaultdict, deque
from django.db import transaction
from django.utils.timezone import now
def generate_workflow(workflow_template, company, created_by):
    from .models import TemplateDependency
    from .models import WorkflowInstance

    template_to_task = {}
    durations = {}
    with transaction.atomic():
        workflow_template.last_deployed = now()
        workflow = WorkflowInstance.objects.create(template=workflow_template, company=company, created_by=created_by, status='active')
        for t_task in workflow_template.template_tasks.all():
            task = Task.objects.create(title=t_task.title, description=t_task.description, company=company,
                created_by=created_by,status='pending', workflow_instance=workflow)
            task.create_group_chat = t_task.chat_group
            task.assigned_to.set(list(t_task.assignee.all()))
            template_to_task[t_task.id] = task
            durations[task] = timedelta(days=t_task.duration)
    
        graph = defaultdict(list)
        degree_of_dependency =  {task: 0 for task in template_to_task.values()}
        
        for dep in TemplateDependency.objects.filter(from_task__template = workflow_template):
                from_task = template_to_task[dep.from_task.id]
                to_task = template_to_task[dep.to_task.id]
                graph[from_task].append([to_task, dep.dependency_type, dep.to_task.duration])
                degree_of_dependency[to_task] += 1
        
        queue = deque([task for task in template_to_task.values() if degree_of_dependency[task] == 0])
        
        for task in queue:
            task.start_date = now()
            task.end_date = now() + durations[task]
            task.save()

        sorted_tasks = []
        while queue:
            from_task = queue.popleft()
            sorted_tasks.append(from_task)

            for to_task, dep_type, dur_days in graph[from_task]:
                duration = timedelta(days=dur_days)

                if dep_type == 'finish_to_start':
                    to_task.start_date = max(to_task.start_date or from_task.end_date, from_task.end_date)
                    to_task.end_date = to_task.start_date + duration

                elif dep_type == 'start_to_start':
                    to_task.start_date = max(to_task.start_date or from_task.start_date, from_task.start_date)
                    to_task.end_date = to_task.start_date + duration

                elif dep_type == 'finish_to_finish':
                    to_task.end_date = max(to_task.end_date or from_task.end_date, from_task.end_date)
                    to_task.start_date = to_task.end_date - duration

                elif dep_type == 'start_to_finish':
                    to_task.end_date = max(to_task.end_date or from_task.start_date, from_task.start_date)
                    to_task.start_date = to_task.end_date - duration

                to_task.save()

                TaskDependency.objects.create(from_task=from_task,to_task=to_task,dependency_type=dep_type, company=company)

                degree_of_dependency[to_task] -= 1
                if degree_of_dependency[to_task] == 0:
                    queue.append(to_task)
    
        if len(sorted_tasks) != len(template_to_task):
            raise ValueError("Circular dependency detected in workflow template")

        return list(template_to_task.values())



def has_circular_template_task(from_template, to_template=None, visited=None):
    from .models import TemplateDependency
    if visited is None:
        visited = set()
    
    if to_template.id in visited:
        return False
    
    visited.add(to_template.id)

    dependencies = TemplateDependency.objects.filter(from_task=to_template)
    for dep in dependencies:
        next_template = dep.to_task
        if  from_template == next_template:
            return True
        if has_circular_template_task(from_template, next_template, visited):
            return True
        
    return False


        