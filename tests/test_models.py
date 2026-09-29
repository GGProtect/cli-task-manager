from datetime import date, datetime, timedelta

import pytest

from task_manager.models import Task


def test_task_uses_default_values() -> None:
    task = Task(title="Write tests")

    assert task.id is None
    assert task.priority is None
    assert task.deadline is None
    assert task.status == "todo"
    assert isinstance(task.created_at, datetime)


def test_task_accepts_valid_values() -> None:
    deadline = date.today() + timedelta(days=1)

    task = Task(
        title="Write tests",
        priority=3,
        deadline=deadline,
        status="in_progress",
    )

    assert task.priority == 3
    assert task.deadline == deadline
    assert task.status == "in_progress"


@pytest.mark.parametrize("title", ["", "   "])
def test_task_rejects_empty_title(title: str) -> None:
    with pytest.raises(ValueError):
        Task(title=title)


@pytest.mark.parametrize("priority", [0, 6])
def test_task_rejects_priority_outside_allowed_range(priority: int) -> None:
    with pytest.raises(ValueError):
        Task(title="Write tests", priority=priority)


def test_task_rejects_invalid_status() -> None:
    with pytest.raises(ValueError):
        Task(title="Write tests", status="cancelled")


def test_task_is_overdue_with_past_deadline_and_unfinished_status() -> None:
    task = Task(
        title="Write tests",
        deadline=date.today() - timedelta(days=1),
    )

    assert task.is_overdue is True


def test_task_is_not_overdue_without_deadline() -> None:
    task = Task(title="Write tests")

    assert task.is_overdue is False


def test_task_is_not_overdue_on_deadline_date() -> None:
    task = Task(title="Write tests", deadline=date.today())

    assert task.is_overdue is False


def test_done_task_is_not_overdue() -> None:
    task = Task(
        title="Write tests",
        deadline=date.today() - timedelta(days=1),
        status="done",
    )

    assert task.is_overdue is False


def test_task_is_not_overdue_with_future_deadline() -> None:
    task = Task(
        title="Write tests",
        deadline=date.today() + timedelta(days=1),
    )

    assert task.is_overdue is False
