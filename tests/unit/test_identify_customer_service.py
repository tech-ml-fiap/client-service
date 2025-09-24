import pytest
from unittest.mock import MagicMock, patch

from app.domain.services.identify_customer_service import IdentifyCustomerService
from app.domain.entities.customer import Customer
from app.domain.value_objects.cpf import CPF
from app.domain.value_objects.email import Email


@pytest.fixture
def fake_customer():
    return Customer(
        id=1,
        name="John Doe",
        cpf=CPF("848.354.160-23"),
        email=Email("john@example.com"),
        password_hash="hashed123",
        active=True,
    )


@pytest.fixture
def repo_mock(fake_customer):
    repo = MagicMock()
    repo.find_by_email.return_value = None
    repo.find_by_cpf.return_value = fake_customer
    return repo


@pytest.fixture
def hasher_mock():
    hasher = MagicMock()
    hasher.verify.return_value = True
    return hasher


def test_identify_success(repo_mock, hasher_mock, fake_customer):
    with patch(
        "app.domain.services.identify_customer_service.create_access_token"
    ) as jwt_mock:
        jwt_mock.return_value = "jwt-token"

        service = IdentifyCustomerService(repo_mock, hasher_mock)
        token = service.execute(fake_customer.cpf.value, "plain-password")

        assert token == "jwt-token"
        repo_mock.find_by_cpf.assert_called_once_with(fake_customer.cpf.value)
        hasher_mock.verify.assert_called_once_with(
            "plain-password", fake_customer.password_hash
        )
        jwt_mock.assert_called_once()
        # Confere se payload enviado ao JWT tem os campos certos
        args, kwargs = jwt_mock.call_args
        payload = args[0]
        assert payload["id"] == fake_customer.id
        assert payload["cpf"] == fake_customer.cpf.value
        assert payload["email"] == fake_customer.email.value
        assert payload["name"] == fake_customer.name
        assert payload["role"] == "customer"


def test_identify_success_with_email(repo_mock, hasher_mock, fake_customer):
    repo_mock.find_by_email.return_value = fake_customer
    repo_mock.find_by_cpf.return_value = None
    with patch(
        "app.domain.services.identify_customer_service.create_access_token",
        return_value="jwt-token",
    ) as jwt_mock:
        service = IdentifyCustomerService(repo_mock, hasher_mock)
        token = service.execute(fake_customer.email.value, "plain-password")
        assert token == "jwt-token"
        repo_mock.find_by_email.assert_called_once_with(fake_customer.email.value)
        repo_mock.find_by_cpf.assert_not_called()
        jwt_mock.assert_called_once()


def test_customer_not_found(repo_mock, hasher_mock):
    repo_mock.find_by_email.return_value = None
    repo_mock.find_by_cpf.return_value = None
    service = IdentifyCustomerService(repo_mock, hasher_mock)
    with pytest.raises(ValueError, match="Usuário não encontrado ou inativo."):
        service.execute("848.354.160-23", "plain-password")


def test_customer_inactive(repo_mock, hasher_mock, fake_customer):
    fake_customer.active = False
    repo_mock.find_by_cpf.return_value = fake_customer
    service = IdentifyCustomerService(repo_mock, hasher_mock)
    with pytest.raises(ValueError, match="Usuário não encontrado ou inativo."):
        service.execute(fake_customer.cpf.value, "plain-password")


def test_invalid_password(repo_mock, hasher_mock, fake_customer):
    hasher_mock.verify.return_value = False
    repo_mock.find_by_cpf.return_value = fake_customer
    service = IdentifyCustomerService(repo_mock, hasher_mock)
    with pytest.raises(ValueError, match="Credenciais inválidas."):
        service.execute(fake_customer.cpf.value, "wrong-password")
