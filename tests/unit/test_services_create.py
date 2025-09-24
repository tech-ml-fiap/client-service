import pytest

from app.adapters.driven.security.bcrypt_hasher import BcryptPasswordHasher
from app.domain.entities.customer import Customer
from app.domain.services.create_customer_service import CreateCustomerService
from app.domain.value_objects.cpf import CPF
from app.domain.value_objects.email import Email


def test_create_customer_ok(fake_repo):
    svc = CreateCustomerService(fake_repo, BcryptPasswordHasher())
    cust = Customer(
        id=None,
        name="Ana",
        cpf=CPF("12345678909"),
        email=Email("ana@mail.com"),
        password_hash="",
    )
    created = svc.execute(cust, "password1234")
    assert created.id == 1
    assert fake_repo.list_all()  # repo recebeu


def test_create_customer_repeated_cpf(fake_repo):
    svc = CreateCustomerService(fake_repo, BcryptPasswordHasher())
    cust1 = Customer(
        id=None,
        name="A",
        cpf=CPF("12345678909"),
        email=Email("a@mail.com"),
        password_hash="",
    )
    cust2 = Customer(
        id=None,
        name="B",
        cpf=CPF("12345678909"),
        email=Email("b@mail.com"),
        password_hash="",
    )
    svc.execute(cust1, "password1234")
    with pytest.raises(ValueError, match="CPF já cadastrado"):
        svc.execute(cust2, "password1234")
