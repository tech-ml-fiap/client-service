import time
from datetime import timedelta, datetime

import pytest
import jwt

from app.shared.handles.jwt_user import (
    create_access_token,
    verify_jwt,
    get_password_hash,
    verify_password,
    SECRET_KEY,
    ALGORITHM,
)


# ---------- JWT ----------


def test_jwt_roundtrip():
    """Cria token, valida e compara payload."""
    data = {"id": 1, "cpf": "12345678909"}
    token = create_access_token(data, expires_delta=timedelta(minutes=1))

    payload = verify_jwt(token)
    # as chaves originais devem estar presentes
    assert payload["id"] == 1
    assert payload["cpf"] == "12345678909"
    # claim exp foi acrescentado
    assert "exp" in payload
    exp_utc = datetime.utcfromtimestamp(payload["exp"])
    assert exp_utc > datetime.utcnow()


def test_jwt_expired():
    """Token com expiração negativa deve falhar."""
    token = create_access_token({"foo": "bar"}, expires_delta=timedelta(seconds=-1))
    with pytest.raises(ValueError, match="Token expirado"):
        verify_jwt(token)


def test_jwt_invalid_signature():
    """Token assinado com chave errada gera 'Token inválido'."""
    wrong_token = jwt.encode({"some": "payload"}, "other_key", algorithm=ALGORITHM)
    with pytest.raises(ValueError, match="Token inválido"):
        verify_jwt(wrong_token)


# ---------- Password ----------


def test_password_hash_and_verify():
    raw = "Secr3t!"
    hashed = get_password_hash(raw)

    assert hashed != raw  # de fato foi hasheado
    assert verify_password(raw, hashed) is True
    assert verify_password("wrong-pass", hashed) is False
