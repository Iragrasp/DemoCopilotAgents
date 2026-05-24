"""
models/user.py  — open this file AND services/user_service.py in VS Code tabs.
Copilot reads both and understands the User type when generating UserService methods.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal


@dataclass
class User:
    id: str
    email: str
    role: Literal["admin", "viewer", "editor"]
    name: str
    active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)

    def __repr__(self):
        return f"User(id={self.id!r}, email={self.email!r}, role={self.role!r})"
