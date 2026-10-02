from datetime import date, timedelta
from pathlib import Path

import pytest

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
