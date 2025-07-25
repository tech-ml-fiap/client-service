from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_post_customer_and_list():
    r = client.post(
        "api/client",
        json={"name": "Ana", "cpf": "123.456.789-09", "email": "ana@mail.com"},
    )
    assert r.status_code == 201
    cust = r.json()
    assert cust["cpf"] == "123.456.789-09"

    r = client.get("api/client")
    assert r.status_code == 200
    assert len(r.json()) == 1
