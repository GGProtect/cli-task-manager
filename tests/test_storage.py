from datetime import date, datetime
from pathlib import Path

import pytest

from task_manager.models import Task
from task_manager.storage import SQLiteTaskStorage


def test_initialize_creates_database_and_empty_tasks_table(tmp_path: Path) -> None:
    database_path = tmp_path / "data" / "tasks.db"
    storage = SQLiteTaskStorage(str(database_path))

    storage.initialize()

    assert database_path.is_file()
    assert storage.get_all_tasks() == []


def test_save_task_assigns_id(tmp_path: Path) -> None:
    storage = SQLiteTaskStorage(str(tmp_path / "tasks.db"))
    storage.initialize()
    task = Task(title="Write storage tests")

    saved_task = storage.save_task(task)

    assert saved_task is task
    assert task.id is not None


def test_get_all_tasks_returns_saved_tasks_with_original_types(tmp_path: Path) -> None:
    storage = SQLiteTaskStorage(str(tmp_path / "tasks.db"))
    storage.initialize()
    first_task = Task(
        title="Write storage tests",
        created_at=datetime(2026, 9, 30, 10, 0, 0),
    )
    second_task = Task(
        title="Review storage tests",
        priority=5,
        deadline=date(2026, 10, 1),
        status="in_progress",
        created_at=datetime(2026, 9, 30, 11, 0, 0),
    )
    storage.save_task(first_task)
    storage.save_task(second_task)

    loaded_tasks = storage.get_all_tasks()
    loaded_tasks_by_id = {task.id: task for task in loaded_tasks}

    assert loaded_tasks_by_id[first_task.id] == first_task
    assert loaded_tasks_by_id[second_task.id] == second_task


def test_save_task_rejects_task_with_existing_id(tmp_path: Path) -> None:
    storage = SQLiteTaskStorage(str(tmp_path / "tasks.db"))
    storage.initialize()
    task = Task(title="Write storage tests", id=1)

    with pytest.raises(ValueError):
        storage.save_task(task)


def test_get_task_by_id_returns_saved_task(tmp_path: Path) -> None:
    storage = SQLiteTaskStorage(str(tmp_path / "tasks.db"))
    storage.initialize()
    task = Task(
        title="Find a task",
        deadline=date(2026, 10, 1),
        created_at=datetime(2026, 9, 30, 12, 0, 0),
    )
    storage.save_task(task)

    loaded_task = storage.get_task_by_id(task.id)

    assert loaded_task == task


def test_get_task_by_id_returns_none_for_unknown_id(tmp_path: Path) -> None:
    storage = SQLiteTaskStorage(str(tmp_path / "tasks.db"))
    storage.initialize()

    assert storage.get_task_by_id(999) is None


def test_update_task_updates_existing_task(tmp_path: Path) -> None:
    storage = SQLiteTaskStorage(str(tmp_path / "tasks.db"))
    storage.initialize()
    task = Task(
        title="Original title",
        priority=1,
        created_at=datetime(2026, 9, 30, 12, 0, 0),
    )
    storage.save_task(task)
    task.title = "Updated title"
    task.priority = 5
    task.deadline = date(2026, 10, 1)
    task.status = "in_progress"

    was_updated = storage.update_task(task)
    loaded_task = storage.get_task_by_id(task.id)

    assert was_updated is True
    assert loaded_task == task


def test_update_task_returns_false_for_unknown_id(tmp_path: Path) -> None:
    storage = SQLiteTaskStorage(str(tmp_path / "tasks.db"))
    storage.initialize()
    task = Task(title="Unknown task", id=999)

    assert storage.update_task(task) is False


def test_update_task_rejects_task_without_id(tmp_path: Path) -> None:
    storage = SQLiteTaskStorage(str(tmp_path / "tasks.db"))
    storage.initialize()

    with pytest.raises(ValueError):
        storage.update_task(Task(title="Unsaved task"))


def test_delete_task_removes_existing_task(tmp_path: Path) -> None:
    storage = SQLiteTaskStorage(str(tmp_path / "tasks.db"))
    storage.initialize()
    task = Task(title="Delete a task")
    storage.save_task(task)

    was_deleted = storage.delete_task(task.id)

    assert was_deleted is True
    assert storage.get_task_by_id(task.id) is None


def test_delete_task_returns_false_for_unknown_id(tmp_path: Path) -> None:
    storage = SQLiteTaskStorage(str(tmp_path / "tasks.db"))
    storage.initialize()

    assert storage.delete_task(999) is False
