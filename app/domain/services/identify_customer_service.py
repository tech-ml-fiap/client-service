from app.domain.ports import CustomerRepositoryPort
from app.domain.value_objects.cpf import CPF
from app.shared.handles.jwt_user import create_access_token


class IdentifyCustomerService:
    def __init__(self, repo: CustomerRepositoryPort):
        self.repo = repo

    def execute(self, cpf: str) -> str:
        clean_cpf = CPF(cpf).value
        customer  = self.repo.find_by_cpf(clean_cpf)
        if not customer or not customer.active:
            raise ValueError("CPF não encontrado ou inativo.")

        payload = {
            "id": customer.id,
            "cpf": customer.cpf.value,
            "email": customer.email.value,
            "name": customer.name,
            "role": "customer",
        }
        return create_access_token(payload)
