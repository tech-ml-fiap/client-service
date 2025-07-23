from app.domain.entities.customer import Customer
from app.domain.ports import CustomerRepositoryPort
from app.domain.value_objects.cpf import CPF


class CreateCustomerService:
    def __init__(self, repo: CustomerRepositoryPort):
        self.repo = repo

    @staticmethod
    def _digits_only(cpf: str) -> str:
        return "".join(ch for ch in cpf if ch.isdigit())

    def execute(self, customer: Customer) -> Customer:
        if self.repo.find_by_cpf(customer.cpf.value):
            raise ValueError("CPF já cadastrado no sistema.")
        if self.repo.find_by_email(customer.email.value):
            raise ValueError("E-mail já cadastrado no sistema.")
        customer.cpf = CPF(self._digits_only(customer.cpf.value))
        return self.repo.create(customer)
