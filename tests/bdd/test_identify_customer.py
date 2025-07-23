# tests/bdd/test_identify_customer.py
from pytest_bdd import scenario, given, when, then, parsers
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


@scenario("features/identify_customer.feature", "Cliente existente recebe JWT")
def test_identify_customer():
    ...


@given(parsers.parse('existe um cliente com CPF "{cpf}"'))
def criar_cliente(cpf):
    client.post(
        "api/client",
        json={"name": "Ana", "cpf": cpf, "email": "ana@mail.com"},
    )


@when(
    parsers.parse('eu faço uma requisição GET em "{url}"'),
    target_fixture="do_request",
)
def do_request(url):
    """Executa a requisição GET e devolve o Response."""
    return client.get(url)


@then("a resposta tem status 200")
def check_status(do_request):
    assert do_request.status_code == 200


@then('o JSON contém o campo "jwt"')
def check_json(do_request):
    assert "jwt" in do_request.json()
