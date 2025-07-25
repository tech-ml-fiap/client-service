import pytest

from app.domain.value_objects.cpf import CPF
from app.domain.value_objects.email import Email


@pytest.mark.parametrize("cpf", ["12345678909", "123.456.789-09"])
def test_cpf_ok(cpf):
    vo = CPF(cpf)
    assert vo.value == "12345678909"
    assert vo.formatted() == "123.456.789-09"


@pytest.mark.parametrize("cpf", ["123", "111.111.111-11"])
def test_cpf_fail(cpf):
    with pytest.raises(ValueError):
        CPF(cpf)


def test_email_ok():
    e = Email("ana@mail.com")
    assert str(e) == "ana@mail.com"


@pytest.mark.parametrize("invalid", ["ana", "ana@", "@test.com"])
def test_email_fail(invalid):
    with pytest.raises(ValueError):
        Email(invalid)
