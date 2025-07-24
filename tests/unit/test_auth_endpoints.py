# tests/unit/test_auth_endpoints.py

import pytest
from fastapi.testclient import TestClient
from datetime import timedelta

from main import app
from app.shared.handles.jwt_user import create_access_token

client = TestClient(app)


@pytest.fixture(autouse=True)
def override_db():
    """
    Override global de get_db() para usar SQLite em memória
    recriado antes de CADA teste.
    """
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.pool import StaticPool
    from database import Base
    from app.adapters.driver.dependencies import get_db

    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)

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


def test_verify_missing_token():
    r = client.post("/api/auth", json={"token": ""})
    assert r.status_code == 400
    assert r.json()["detail"] == "Token ausente"


def test_verify_malformed_token():
    r = client.post("/api/auth", json={"token": "not.a.jwt"})
    assert r.status_code == 401
    assert "Token inválido" in r.json()["detail"]


def test_verify_expired_token():
    tok = create_access_token(
        {"cpf": "12345678909"}, expires_delta=timedelta(seconds=-1)
    )
    r = client.post("/api/auth", json={"token": tok})
    assert r.status_code == 401
    assert r.json()["detail"] == "Token expirado"


def test_verify_token_without_cpf():
    tok = create_access_token({"foo": "bar"})
    r = client.post("/api/auth", json={"token": tok})
    assert r.status_code == 400
    assert r.json()["detail"] == "Token não contém CPF"


def test_verify_token_customer_not_found():
    # sem criar cliente
    tok = create_access_token({"cpf": "12345678909", "email": "x@y.com", "name": "X"})
    r = client.post("/api/auth", json={"token": tok})
    assert r.status_code == 404
    assert r.json()["detail"] == "Cliente não encontrado ou inativo"


def test_verify_token_success():
    # 1) cria o cliente
    cr = client.post(
        "/api/client",
        json={"name": "Ana", "cpf": "123.456.789-09", "email": "ana@mail.com"},
    )
    assert cr.status_code == 201

    # 2) gera token
    payload = {"cpf": "12345678909", "email": "ana@mail.com", "name": "Ana"}
    tok = create_access_token(payload)

    # 3) verifica
    r = client.post("/api/auth", json={"token": tok})
    assert r.status_code == 200

    body = r.json()
    assert body["id"] == cr.json()["id"]
    assert body["cpf"] == "123.456.789-09"
    assert body["email"] == "ana@mail.com"
    assert body["name"] == "Ana"
