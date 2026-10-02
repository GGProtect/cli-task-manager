from datetime import date, timedelta
from pathlib import Path

import pytest

from task_manager.models import Task
from task_manager.service import TaskService
from task_manager.storage import SQLiteTaskStorage


def _create_service(tmp_path: Path) -> TaskService:
    storage = SQLiteTaskStorage(str(tmp_path / "tasks.db"))
    storage.initialize()
    return TaskService(storage)


def test_create_task_saves_task_and_assigns_id(tmp_path: Path) -> None:
    service = _create_service(tmp_path)

    task = service.create_task(title="Create service tests")

    assert task.id is not None
    assert service.get_tasks() == [task]


def test_create_task_accepts_deadline_tomorrow(tmp_path: Path) -> None:
    service = _create_service(tmp_path)
    deadline = date.today() + timedelta(days=1)

    task = service.create_task(title="Create service tests", deadline=deadline)

    assert task.deadline == deadline


def test_create_task_rejects_deadline_today(tmp_path: Path) -> None:
    service = _create_service(tmp_path)

    with pytest.raises(ValueError):
        service.create_task(title="Create service tests", deadline=date.today())


def test_create_task_rejects_deadline_in_the_past(tmp_path: Path) -> None:
    service = _create_service(tmp_path)
    deadline = date.today() - timedelta(days=1)

    with pytest.raises(ValueError):
        service.create_task(title="Create service tests", deadline=deadline)


def test_get_tasks_returns_created_tasks(tmp_path: Path) -> None:
    service = _create_service(tmp_path)
    first_task = service.create_task(title="First task")
    second_task = service.create_task(title="Second task")

    tasks = service.get_tasks()
    tasks_by_id = {task.id: task for task in tasks}

    assert tasks_by_id[first_task.id] == first_task
    assert tasks_by_id[second_task.id] == second_task


def test_change_task_status_updates_existing_task(tmp_path: Path) -> None:
    service = _create_service(tmp_path)
    task = service.create_task(title="Change task status")

    updated_task = service.change_task_status(task.id, "in_progress")

    assert updated_task is not None
    assert updated_task.status == "in_progress"
    assert service.storage.get_task_by_id(task.id).status == "in_progress"


def test_change_task_status_returns_none_for_unknown_id(tmp_path: Path) -> None:
    service = _create_service(tmp_path)

    assert service.change_task_status(999, "done") is None


def test_change_task_status_rejects_invalid_status(tmp_path: Path) -> None:
    service = _create_service(tmp_path)
    task = service.create_task(title="Change task status")

    with pytest.raises(ValueError):
        service.change_task_status(task.id, "cancelled")


def test_delete_task_removes_existing_task(tmp_path: Path) -> None:
    service = _create_service(tmp_path)
    task = service.create_task(title="Delete task")

    was_deleted = service.delete_task(task.id)

    assert was_deleted is True
    assert service.get_tasks() == []


def test_delete_task_returns_false_for_unknown_id(tmp_path: Path) -> None:
    service = _create_service(tmp_path)

    assert service.delete_task(999) is False


def test_filter_tasks_by_status(tmp_path: Path) -> None:
    service = _create_service(tmp_path)
    todo_task = service.create_task(title="Todo task")
    in_progress_task = service.create_task(title="In progress task")
    service.change_task_status(in_progress_task.id, "in_progress")

    filtered_tasks = service.filter_tasks(status="todo")

    assert filtered_tasks == [todo_task]


def test_filter_tasks_by_priority(tmp_path: Path) -> None:
    service = _create_service(tmp_path)
    low_priority_task = service.create_task(title="Low priority task", priority=1)
    high_priority_task = service.create_task(title="High priority task", priority=5)

    filtered_tasks = service.filter_tasks(priority=5)

    assert filtered_tasks == [high_priority_task]
    assert low_priority_task not in filtered_tasks


def test_filter_tasks_returns_only_overdue_tasks(tmp_path: Path) -> None:
    service = _create_service(tmp_path)
    overdue_task = Task(
        title="Overdue task",
        deadline=date.today() - timedelta(days=1),
    )
    service.storage.save_task(overdue_task)
    service.create_task(
        title="Future task",
        deadline=date.today() + timedelta(days=1),
    )

    filtered_tasks = service.filter_tasks(only_overdue=True)

    assert filtered_tasks == [overdue_task]


def test_filter_tasks_by_deadline_presence(tmp_path: Path) -> None:
    service = _create_service(tmp_path)
    task_without_deadline = service.create_task(title="Task without deadline")
    task_with_deadline = service.create_task(
        title="Task with deadline",
        deadline=date.today() + timedelta(days=1),
    )

    tasks_with_deadline = service.filter_tasks(has_deadline=True)
    tasks_without_deadline = service.filter_tasks(has_deadline=False)

    assert tasks_with_deadline == [task_with_deadline]
    assert tasks_without_deadline == [task_without_deadline]


def test_filter_tasks_combines_multiple_conditions(tmp_path: Path) -> None:
    service = _create_service(tmp_path)
    matching_task = Task(
        title="Matching task",
        priority=3,
        deadline=date.today() - timedelta(days=1),
    )
    service.storage.save_task(matching_task)
    service.create_task(title="Different priority", priority=1)
    service.create_task(
        title="Future deadline",
        priority=3,
        deadline=date.today() + timedelta(days=1),
    )

    filtered_tasks = service.filter_tasks(
        status="todo",
        priority=3,
        only_overdue=True,
        has_deadline=True,
    )

    assert filtered_tasks == [matching_task]


def test_filter_tasks_rejects_invalid_status(tmp_path: Path) -> None:
    service = _create_service(tmp_path)

    with pytest.raises(ValueError):
        service.filter_tasks(status="cancelled")


@pytest.mark.parametrize("priority", [0, 6])
def test_filter_tasks_rejects_invalid_priority(tmp_path: Path, priority: int) -> None:
    service = _create_service(tmp_path)

    with pytest.raises(ValueError):
        service.filter_tasks(priority=priority)
