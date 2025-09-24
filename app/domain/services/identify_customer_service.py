from app.domain.ports import CustomerRepositoryPort
from app.domain.ports.password_hasher import PasswordHasher
from app.domain.value_objects.cpf import CPF
from app.shared.handles.jwt_user import create_access_token


class IdentifyCustomerService:
    def __init__(self, repo: CustomerRepositoryPort, hasher: PasswordHasher):
        self.repo = repo
        self.hasher = hasher

    def execute(self, identifier: str, password: str) -> str:
        customer = self.repo.find_by_email(identifier) or self.repo.find_by_cpf(
            CPF(identifier).value
        )
        if not customer or not customer.active:
            raise ValueError("Usuário não encontrado ou inativo.")

        if not self.hasher.verify(password, customer.password_hash):
            raise ValueError("Credenciais inválidas.")

        payload = {
            "id": customer.id,
            "cpf": customer.cpf.value,
            "email": customer.email.value,
            "name": customer.name,
            "role": "customer",
        }
        return create_access_token(payload)
