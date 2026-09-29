from dataclasses import dataclass, field
from datetime import date, datetime

@dataclass
class Task:
    title: str
    priority: int | None = None
    deadline: date | None = None
    status: str = "todo"
    created_at: datetime = field(default_factory=datetime.now)
    id: int | None = None

    def __post_init__(self) -> None:
        if not self.title or not self.title.strip():
            raise ValueError("Title cannot be empty")
        
        if self.priority is not None and not 1 <= self.priority <= 5:
            raise ValueError("Priority must be in range from 1 to 5")
        
        if self.status not in ("todo", "in_progress", "done"):
            raise ValueError("Status must be one of the following (todo, in_progress, done)")

    @property
    def is_overdue(self) -> bool:
        if self.deadline is None:
            return False

        if self.status == "done":
            return False

        return date.today() > self.deadline
