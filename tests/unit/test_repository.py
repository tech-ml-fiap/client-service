import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.domain.value_objects.cpf import CPF
from app.domain.value_objects.email import Email
from database import Base
from app.adapters.driven.repositories.customer import CustomerRepository
from app.domain.entities.customer import Customer


@pytest.fixture
def session():
    # engine em memória thread-safe
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    db = Session()
    yield db
    db.close()
    engine.dispose()


@pytest.fixture
def repo(session):
    return CustomerRepository(session)


def test_find_by_id_not_exists(repo):
    assert repo.find_by_id(999) is None


def test_create_and_find_by_id(repo):
    cust = Customer(
        id=None,
        name="Alice",
        cpf=CPF("12345678909"),
        email=Email("alice@mail.com"),
    )
    created = repo.create(cust)

    found = repo.find_by_id(created.id)
    assert found is not None
    assert found.id == created.id
    assert found.name == "Alice"
    assert found.cpf.value == "12345678909"


def test_update_success(repo):
    cust = Customer(
        id=None,
        name="Bob",
        cpf=CPF("12345678909"),
        email=Email("bob@mail.com"),
    )
    created = repo.create(cust)

    # altera somente o nome e o flag active
    created.name = "Bobby"
    created.active = False
    updated = repo.update(created)

    assert updated.id == created.id
    assert updated.name == "Bobby"
    assert updated.active is False


def test_update_not_found(repo):
    fake = Customer(
        id=555,
        name="Nobody",
        cpf=CPF("12345678909"),
        email=Email("no@mail.com"),
    )
    with pytest.raises(ValueError, match="Customer not found"):
        repo.update(fake)


def test_delete(repo):
    cust = Customer(
        id=None,
        name="Carol",
        cpf=CPF("12345678909"),
        email=Email("carol@mail.com"),
    )
    created = repo.create(cust)

    # existe antes de deletar
    assert repo.find_by_id(created.id) is not None

    repo.delete(created.id)

    # deve sumir
    assert repo.find_by_id(created.id) is None
