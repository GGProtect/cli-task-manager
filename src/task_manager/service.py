from datetime import date, timedelta

from task_manager.models import Task
from task_manager.storage import SQLiteTaskStorage


class TaskService:
    def __init__(self, storage: SQLiteTaskStorage) -> None:
        self.storage = storage

    def create_task(
        self,
        title: str,
        priority: int | None = None,
        deadline: date | None = None,
    ) -> Task:
        today = date.today()
        minimum_deadline = today + timedelta(days=1)
        if deadline is not None and deadline < minimum_deadline:
            raise ValueError("Deadline must be at least tomorrow")
        task = Task(title=title, priority=priority, deadline=deadline)
        task = self.storage.save_task(task)
        return task
    
    def get_tasks(self) -> list[Task]:
        tasks = self.storage.get_all_tasks()
        return tasks

    def change_task_status(self, task_id: int, new_status: str) -> Task | None:
        task = self.storage.get_task_by_id(task_id=task_id)
        if task is None:
            return None
        if new_status not in ("todo", "in_progress", "done"):
            raise ValueError("Invalid task status")
        task.status = new_status
        if not self.storage.update_task(task):
            return None
        return task

    def delete_task(self, task_id: int) -> bool:
        return self.storage.delete_task(task_id=task_id)

    def filter_tasks(
        self,
        status: str | None = None,
        priority: int | None = None,
        only_overdue: bool = False,
        has_deadline: bool | None = None,
    ) -> list[Task]:
        if status is not None and status not in ("todo", "in_progress", "done"):
            raise ValueError("Invalid task status")

        if priority is not None and not 1 <= priority <= 5:
            raise ValueError("Priority must be in range from 1 to 5")

        tasks = self.get_tasks()
        filtered_tasks = []

        for task in tasks:
            if (
                (status is None or task.status == status)
                and (priority is None or task.priority == priority)
                and (not only_overdue or task.is_overdue)
                and (has_deadline is None or (task.deadline is not None) == has_deadline)
            ):
                filtered_tasks.append(task)

        return filtered_tasks
