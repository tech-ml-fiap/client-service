import pytest
from app.domain.entities.customer import Customer
from app.domain.services.update_customer_service import UpdateCustomerService
from app.domain.value_objects.cpf import CPF
from app.domain.value_objects.email import Email


class FakeRepo:
    def __init__(self, mapping_by_cpf=None, mapping_by_email=None):
        # mapeia cpf → Customer e email → Customer
        self.mapping_by_cpf = mapping_by_cpf or {}
        self.mapping_by_email = mapping_by_email or {}
        self.updated = None

    def find_by_cpf(self, cpf: str):
        return self.mapping_by_cpf.get(cpf)

    def find_by_email(self, email: str):
        return self.mapping_by_email.get(email)

    def update(self, customer: Customer) -> Customer:
        # armazena o cliente recebido e retorna
        self.updated = customer
        return customer


def make_customer(
    id=1,
    name="Original",
    cpf_value="12345678909",
    email_value="orig@mail.com",
    active=True,
):
    return Customer(
        id=id,
        name=name,
        cpf=CPF(cpf_value),
        email=Email(email_value),
        active=active,
    )


def test_validate_updates_invalid_field():
    repo = FakeRepo(mapping_by_cpf={"12345678909": make_customer()})
    svc = UpdateCustomerService(repo)
    with pytest.raises(ValueError, match="Campos inválidos: foo"):
        svc.execute("12345678909", {"foo": "bar"})


def test_customer_not_found():
    repo = FakeRepo(mapping_by_cpf={})
    svc = UpdateCustomerService(repo)
    with pytest.raises(ValueError, match="Cliente não encontrado."):
        svc.execute("12345678909", {})


def test_cpf_duplicate():
    existing = make_customer(id=1, cpf_value="12345678909")
    duplicate = make_customer(id=2, cpf_value="52998224725")
    repo = FakeRepo(
        mapping_by_cpf={
            "12345678909": existing,
            "52998224725": duplicate,
        },
        mapping_by_email={
            "orig@mail.com": existing,
            "dup@mail.com": duplicate,
        },
    )
    svc = UpdateCustomerService(repo)
    # tenta mudar para um CPF já em uso
    with pytest.raises(ValueError, match="CPF já cadastrado."):
        svc.execute("12345678909", {"cpf": "529.982.247-25"})


def test_email_duplicate():
    existing = make_customer(id=1, email_value="orig@mail.com")
    duplicate = make_customer(id=2, email_value="dup@mail.com")
    repo = FakeRepo(
        mapping_by_cpf={"12345678909": existing},
        mapping_by_email={
            "orig@mail.com": existing,
            "dup@mail.com": duplicate,
        },
    )
    svc = UpdateCustomerService(repo)
    with pytest.raises(ValueError, match="E-mail já cadastrado."):
        svc.execute("12345678909", {"email": "dup@mail.com"})


def test_success_update_name_active():
    existing = make_customer()
    repo = FakeRepo(
        mapping_by_cpf={"12345678909": existing},
        mapping_by_email={"orig@mail.com": existing},
    )
    svc = UpdateCustomerService(repo)

    updated = svc.execute("123.456.789-09", {"name": "NewName", "active": False})

    assert updated.name == "NewName"
    assert updated.active is False
    # garante que o repositório recebeu o objeto modificado
    assert repo.updated.name == "NewName"
    assert repo.updated.active is False


def test_success_update_cpf_and_email():
    existing = make_customer()
    repo = FakeRepo(
        mapping_by_cpf={"12345678909": existing},
        mapping_by_email={"orig@mail.com": existing},
    )
    svc = UpdateCustomerService(repo)

    new_cpf = "529.982.247-25"
    new_email = "new@mail.com"
    updated = svc.execute("123.456.789-09", {"cpf": new_cpf, "email": new_email})

    assert updated.cpf.value == "52998224725"
    assert updated.email.value == new_email
    assert repo.updated.cpf.value == "52998224725"
    assert repo.updated.email.value == new_email
