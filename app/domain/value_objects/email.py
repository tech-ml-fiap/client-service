from __future__ import annotations
from dataclasses import dataclass
import re

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@dataclass(frozen=True, slots=True)
class Email:
    value: str

    def __post_init__(self) -> None:
        if not _EMAIL_RE.match(self.value):
            raise ValueError("E-mail inválido")

    def __str__(self) -> str:
        return self.value
