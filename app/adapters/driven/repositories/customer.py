import re
from typing import List, Optional
from sqlalchemy.orm import Session

from app.adapters.driven.models.customer_model import CustomerModel
from app.domain.entities.customer import Customer
from app.domain.ports.customer_repository_port import CustomerRepositoryPort
from app.domain.value_objects.cpf import CPF
from app.domain.value_objects.email import Email

_DIGITS_RE = re.compile(r"\D+")


class CustomerRepository(CustomerRepositoryPort):
    """Implementação SQLAlchemy da porta CustomerRepositoryPort."""

    def __init__(self, session: Session):
        self.session = session

    # ---------- helpers ----------
    @staticmethod
    def _to_domain(model: CustomerModel) -> Customer:
        return Customer(
            id=model.id,
            name=model.name,
            cpf=CPF(model.cpf),
            email=Email(model.email),
            active=model.active,
            created_at=model.created_at,
            updated_at=model.updated_at,
            password_hash=model.password_hash,
        )

    @staticmethod
    def _sanitize_cpf(raw_cpf: str) -> str:
        """Mantém somente dígitos para persistir/consultar."""
        return _DIGITS_RE.sub("", raw_cpf)

    # ---------- C ----------
    def create(self, customer: Customer) -> Customer:
        model = CustomerModel(
            name=customer.name,
            cpf=self._sanitize_cpf(customer.cpf.value),
            email=customer.email.value,
            password_hash=customer.password_hash,
        )
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return self._to_domain(model)

    # ---------- R ----------
    def find_by_id(self, customer_id: int) -> Optional[Customer]:
        model = self.session.query(CustomerModel).get(customer_id)
        return self._to_domain(model) if model else None

    def find_by_cpf(self, cpf: str) -> Optional[Customer]:
        digits = self._sanitize_cpf(cpf)
        model = (
            self.session.query(CustomerModel)
            .filter(CustomerModel.cpf == digits)
            .first()
        )
        return self._to_domain(model) if model else None

    def find_by_email(self, email: str) -> Optional[Customer]:
        model = (
            self.session.query(CustomerModel)
            .filter(CustomerModel.email == email)
            .first()
        )
        return self._to_domain(model) if model else None

    def list_all(self) -> List[Customer]:
        """Implementação requerida pela interface."""
        return [self._to_domain(m) for m in self.session.query(CustomerModel).all()]

    # alias opcional – remove se não precisar de compatibilidade
    find_all = list_all

    # ---------- U ----------
    def update(self, customer: Customer) -> Customer:
        model: CustomerModel = self.session.query(CustomerModel).get(customer.id)
        if not model:
            raise ValueError("Customer not found")

        model.name = customer.name
        model.email = customer.email.value
        model.cpf = self._sanitize_cpf(customer.cpf.value)
        model.active = customer.active

        self.session.commit()
        self.session.refresh(model)
        return self._to_domain(model)

    # ---------- D ----------
    def delete(self, customer_id: int) -> None:
        model = self.session.query(CustomerModel).get(customer_id)
        if model:
            self.session.delete(model)
            self.session.commit()
