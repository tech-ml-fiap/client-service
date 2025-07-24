from app.domain.entities.customer import Customer
from app.domain.ports import CustomerRepositoryPort
from app.domain.value_objects.cpf import CPF
from app.domain.value_objects.email import Email


class UpdateCustomerService:
    _allowed = {"cpf", "name", "email", "active"}

    def __init__(self, repo: CustomerRepositoryPort):
        self.repo = repo

    @staticmethod
    def _digits_only(cpf: str) -> str:
        return "".join(ch for ch in cpf if ch.isdigit())

    def _validate_updates(self, updates: dict):
        extra = set(updates) - self._allowed
        if extra:
            raise ValueError(f"Campos inválidos: {', '.join(extra)}")

    def execute(self, cpf: str, updates: dict) -> Customer:
        self._validate_updates(updates)

        # cliente existente
        cust = self.repo.find_by_cpf(self._digits_only(cpf))
        if not cust:
            raise ValueError("Cliente não encontrado.")

        # CPF
        if "cpf" in updates:
            new_cpf = CPF(updates["cpf"])
            if self.repo.find_by_cpf(new_cpf.value) and new_cpf.value != cust.cpf.value:
                raise ValueError("CPF já cadastrado.")
            cust.cpf = new_cpf

        # e-mail
        if "email" in updates:
            new_email = Email(updates["email"])
            if (
                self.repo.find_by_email(new_email.value)
                and new_email.value != cust.email.value
            ):
                raise ValueError("E-mail já cadastrado.")
            cust.email = new_email

        if "name" in updates:
            cust.name = updates["name"]
        if "active" in updates:
            cust.active = updates["active"]

        return self.repo.update(cust)
