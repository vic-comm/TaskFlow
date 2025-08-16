from .models import TaskDependency
def has_circular_task(from_task, to_task, visited=None):
    if visited is None:
        visited = set()
    
    if to_task.id in visited:
        return False
    
    visited.add(to_task.id)

    dependencies = TaskDependency.objects.filter(from_task=to_task)
    for dep in dependencies:
        next_task = dep.to_task
        if  from_task == next_task:
            return True
        if has_circular_task(from_task,next_task, visited):
            return True
        
    return False