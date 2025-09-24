from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.adapters.driven.repositories.customer import CustomerRepository
from app.adapters.driver.controllers.schemas import (
    CustomerOut,
    CustomerIn,
    CustomersOut,
    CustomerIdentifyOut,
    CustomerUpdateIn,
)
from app.domain.entities.customer import Customer
from app.adapters.driver.dependencies import get_db
from app.domain.services.create_customer_service import CreateCustomerService
from app.domain.services.identify_customer_service import IdentifyCustomerService
from app.domain.services.list_customers_service import ListCustomersService
from app.domain.services.update_customer_service import UpdateCustomerService
from app.domain.value_objects.cpf import CPF
from app.domain.value_objects.email import Email

router = APIRouter()


# ---------- helpers ----------
def _to_response(entity: Customer) -> CustomerOut:
    return CustomerOut(
        id=entity.id,
        name=entity.name,
        cpf=entity.cpf.formatted(),
        email=entity.email.value,
        active=entity.active,
    )


# ---------- endpoints ----------
@router.post(
    "",
    response_model=CustomerOut,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {
            "description": (
                "Falha de validação ou regras de negócio.\n\n"
                "- **CPF inválido**\n"
                "- **E-mail inválido**\n"
                "- **CPF já cadastrado**\n"
                "- **E-mail já cadastrado**"
            ),
            "content": {
                "application/json": {
                    "examples": {
                        "cpf_invalido": {
                            "summary": "CPF inválido",
                            "value": {"detail": "CPF inválido."},
                        },
                        "email_invalido": {
                            "summary": "E-mail inválido",
                            "value": {"detail": "E-mail inválido"},
                        },
                        "cpf_duplicado": {
                            "summary": "CPF já cadastrado",
                            "value": {"detail": "CPF já cadastrado no sistema."},
                        },
                        "email_duplicado": {
                            "summary": "E-mail já cadastrado",
                            "value": {"detail": "E-mail já cadastrado no sistema."},
                        },
                    }
                }
            },
        }
    },
)
def create_customer(payload: CustomerIn, db: Session = Depends(get_db)):
    service = CreateCustomerService(CustomerRepository(db))

    try:
        cpf_vo = CPF(payload.cpf)
        email_vo = Email(payload.email)

        customer = Customer(
            id=None,
            name=payload.name,
            cpf=cpf_vo,
            email=email_vo,
        )
        created = service.execute(customer)
        return _to_response(created)

    except ValueError as e:
        # Formato inválido ou duplicidade detectada pelo service
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=List[CustomersOut])
def list_customers(db: Session = Depends(get_db)):
    service = ListCustomersService(CustomerRepository(db))
    customers = service.execute()
    return [
        CustomersOut(
            id=c.id,
            name=c.name,
            cpf=c.cpf.formatted(),
            email=c.email.value,
            active=c.active,
            created_at=c.created_at,
            updated_at=c.updated_at,
        )
        for c in customers
    ]


@router.get(
    "/cpf/{cpf}",
    response_model=CustomerIdentifyOut,
    responses={400: {"description": "CPF inválido ou não encontrado"}},
)
def identify_customer(cpf: str, db: Session = Depends(get_db)):
    service = IdentifyCustomerService(CustomerRepository(db))
    try:
        return CustomerIdentifyOut(jwt=service.execute(cpf))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put(
    "/{cpf}",
    response_model=CustomerOut,
    responses={
        400: {
            "description": (
                "Falha de validação ou regras de negócio.\n\n"
                "- **CPF inválido**\n"
                "- **E-mail inválido**\n"
                "- **CPF já cadastrado**\n"
                "- **E-mail já cadastrado**"
            ),
            "content": {
                "application/json": {
                    "examples": {
                        "cpf_invalido": {
                            "summary": "CPF inválido",
                            "value": {"detail": "CPF inválido."},
                        },
                        "email_invalido": {
                            "summary": "E-mail inválido",
                            "value": {"detail": "E-mail inválido"},
                        },
                        "cpf_duplicado": {
                            "summary": "CPF já cadastrado",
                            "value": {"detail": "CPF já cadastrado."},
                        },
                        "email_duplicado": {
                            "summary": "E-mail já cadastrado",
                            "value": {"detail": "E-mail já cadastrado."},
                        },
                    }
                }
            },
        },
        404: {
            "description": "Cliente não encontrado",
            "content": {
                "application/json": {"example": {"detail": "Cliente não encontrado"}}
            },
        },
    },
)
def update_customer(
    cpf: str,
    payload: CustomerUpdateIn,
    db: Session = Depends(get_db),
):
    """
    Atualiza dados de um cliente identificado pelo **CPF** (11 dígitos ou com máscara).

    Campos permitidos no body: `name`, `email`, `cpf`, `active`.
    """
    service = UpdateCustomerService(CustomerRepository(db))
    updates = payload.model_dump(exclude_unset=True)

    try:
        updated = service.execute(cpf, updates)
        return CustomerOut(
            id=updated.id,
            name=updated.name,
            cpf=updated.cpf.formatted(),
            email=updated.email.value,
            active=updated.active,
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")


@router.delete("/{cpf}", status_code=status.HTTP_204_NO_CONTENT)
def deactivate_customer(cpf: str, db: Session = Depends(get_db)):
    service = UpdateCustomerService(CustomerRepository(db))
    try:
        service.execute(cpf, {"active": False})
        return None
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

@router.get(
    "/{user_id}",
    response_model=CustomerOut,
    responses={
        404: {
            "description": "Cliente não encontrado",
            "content": {"application/json": {"example": {"detail": "Cliente não encontrado"}}},
        }
    },
)
def get_customer_by_id(user_id: int, db: Session = Depends(get_db)):
    repo = CustomerRepository(db)
    customer = repo.find_by_id(user_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return _to_response(customer)


# ---------- rota de teste para “quebrar” o Sonar ----------
@router.get(
    "/teste-sonar",
    summary="Endpoint temporário para falhar no SonarQube",
    tags=["debug"],
)
def teste_sonar(param: str | None = None) -> dict:
    """
    ⚠️ **NÃO USE EM PRODUÇÃO** ⚠️

    Esta rota existe apenas para gerar baixa qualidade de código
    (complexidade, uso de eval, prints, código duplicado, TODO etc.)
    e, assim, forçar a reprovação do PR pelo SonarQube.

    Parâmetros
    ----------
    param : str | None
        Se informado e for “boom”, imprime algo no console;
        caso contrário, faz um cálculo aleatório sem sentido de negócio.
    """
    # TODO remover esta rota antes do merge definitivo               # NOSONAR

    if param is None:  # bloco 1 — código duplicado proposital
        resultado = 0
        for i in range(100):
            resultado += (i**2) % 7
        return {"resultado": resultado, "msg": "sem parâmetro"}

    if param is None:  # bloco 2 — duplicado para sonar reclamar
        resultado = 0
        for i in range(100):
            resultado += (i**2) % 7
        return {"resultado": resultado, "msg": "sem parâmetro"}

    if param == "boom":
        print("💥 Boom!")  # uso de print é code-smell

    try:
        # vulnerabilidade deliberada — Sonar indicará “eval is evil”
        resultado = eval(param)
    except Exception:
        resultado = -1

    return {"resultado": resultado, "param": param}
