from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Iterable, Optional

from app.domain.entities.customer import Customer


class CustomerRepositoryPort(ABC):
    # ---------- C ----------
    @abstractmethod
    def create(self, customer: Customer) -> Customer: ...

    # ---------- R ----------
    @abstractmethod
    def find_by_id(self, customer_id: int) -> Optional[Customer]: ...

    @abstractmethod
    def find_by_cpf(self, cpf: str) -> Optional[Customer]: ...

    @abstractmethod
    def find_by_email(self, email: str) -> Optional[Customer]: ...

    @abstractmethod
    def list_all(self) -> Iterable[Customer]: ...

    # ---------- U ----------
    @abstractmethod
    def update(self, customer: Customer) -> Customer: ...

    # ---------- D ----------
    @abstractmethod
    def delete(self, customer_id: int) -> None: ...
