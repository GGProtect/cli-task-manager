import sqlite3
from datetime import date, datetime
from pathlib import Path

from task_manager.models import Task


class SQLiteTaskStorage:
    def __init__(self, database_path: str = "data/tasks.db") -> None:
        self.database_path = database_path

    def initialize(self) -> None:
        Path(self.database_path).parent.mkdir(parents=True, exist_ok=True)

        connection = sqlite3.connect(self.database_path)
        try:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY,
                    title TEXT NOT NULL,
                    priority INTEGER,
                    deadline TEXT,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            connection.commit()
        finally:
            connection.close()

    def save_task(self, task: Task) -> Task:
        if task.id is not None:
            raise ValueError("Cannot save a task that already has an id")

        connection = sqlite3.connect(self.database_path)
        try:
            cursor = connection.execute(
                """
                INSERT INTO tasks (
                    title,
                    priority,
                    deadline,
                    status,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    task.title,
                    task.priority,
                    task.deadline.isoformat() if task.deadline is not None else None,
                    task.status,
                    task.created_at.isoformat(),
                ),
            )
            task.id = cursor.lastrowid
            connection.commit()
        finally:
            connection.close()

        return task

    def get_all_tasks(self) -> list[Task]:
        connection = sqlite3.connect(self.database_path)
        try:
            rows = connection.execute(
                """
                SELECT id, title, priority, deadline, status, created_at
                FROM tasks
                """
            ).fetchall()
        finally:
            connection.close()

        tasks = []
        for task_id, title, priority, deadline, status, created_at in rows:
            tasks.append(
                Task(
                    id=task_id,
                    title=title,
                    priority=priority,
                    deadline=date.fromisoformat(deadline) if deadline is not None else None,
                    status=status,
                    created_at=datetime.fromisoformat(created_at),
                )
            )

        return tasks

    def get_task_by_id(self, task_id: int) -> Task | None:
        connection = sqlite3.connect(self.database_path)
        try:
            row = connection.execute(
                """
                SELECT id, title, priority, deadline, status, created_at
                FROM tasks
                WHERE id = ?
                """,
                (task_id,),
            ).fetchone()
        finally:
            connection.close()

        if row is None:
            return None

        stored_task_id, title, priority, deadline, status, created_at = row

        return Task(
            id=stored_task_id,
            title=title,
            priority=priority,
            deadline=date.fromisoformat(deadline) if deadline is not None else None,
            status=status,
            created_at=datetime.fromisoformat(created_at),
        )

    def update_task(self, task: Task) -> bool:
        if task.id is None:
            raise ValueError("Cannot update a task without an id")
        
        connection = sqlite3.connect(self.database_path)
        try:
            cursor = connection.execute(
                """
                UPDATE tasks
                SET
                    title = ?,
                    priority = ?,
                    deadline = ?,
                    status = ?
                WHERE id = ?
                """,
                (
                    task.title,
                    task.priority,
                    task.deadline.isoformat() if task.deadline is not None else None,
                    task.status,
                    task.id,
                )
            )
            res = cursor.rowcount
            connection.commit()
        finally:
            connection.close()
        return res > 0

    def delete_task(self, task_id: int) -> bool:
        if task_id is None:
            raise ValueError("Cannot delete a task without an id")

        connection = sqlite3.connect(self.database_path)
        try:
            cursor = connection.execute(
                """
                DELETE FROM tasks
                WHERE id = ?
                """,
                (
                    task_id,
                )
            )  
            res = cursor.rowcount
            connection.commit()
        finally:
            connection.close()

        return res > 0