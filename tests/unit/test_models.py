import pytest
from app.adapters.driven.models.customer_model import CustomerModel

def test_customer_model_repr():
    model = CustomerModel(
        id=42,
        cpf="12345678909",
        name="João",
        email="joao@mail.com",
        active=True
    )
    assert repr(model) == "<Customer(id=42, cpf=12345678909)>"