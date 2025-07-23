"""
Fixtures globais usadas em *todos* os testes.
- Override do banco para os testes que exercitam a API (TestClient).
- Fixtures de repositório em memória para testes unitários.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base
from app.adapters.driven.models import customer_model  # garante criação da tabela
from app.adapters.driven.repositories.customer import CustomerRepository
from app.adapters.driver.dependencies import get_db
from main import app


# ------------------------------------------------------------------
# 1) Override do get_db  ➜  SQLite em memória compartilhado por TestClient
# ------------------------------------------------------------------
@pytest.fixture(autouse=True, scope="session")
def _override_app_db():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)

    TestingSession = sessionmaker(bind=engine, autocommit=False, autoflush=False)

    def _get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _get_db
    yield
    app.dependency_overrides.clear()
    engine.dispose()


# ------------------------------------------------------------------
# 2) Fixtures p/ testes unitários (isolados por função)
# ------------------------------------------------------------------
@pytest.fixture(scope="function")
def in_memory_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    db = Session()
    try:
        yield db
    finally:
        db.close()
        engine.dispose()


@pytest.fixture
def fake_repo(in_memory_session):
    return CustomerRepository(in_memory_session)
