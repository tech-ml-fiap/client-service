from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from app.domain.value_objects.cpf import CPF
from app.domain.value_objects.email import Email


@dataclass(slots=True)
class Customer:

    id: Optional[int]
    name: str
    cpf: CPF
    email: Email
    active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def deactivate(self) -> None:
        self.active = False

    def activate(self) -> None:
        self.active = True
