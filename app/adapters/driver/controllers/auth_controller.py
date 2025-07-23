from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.adapters.driven.repositories.customer import CustomerRepository
from app.adapters.driver.controllers.schemas import TokenVerifyOut, TokenVerifyIn
from app.adapters.driver.dependencies import get_db
from app.domain.value_objects.cpf import CPF
from app.shared.handles.jwt_user import verify_jwt

router = APIRouter()


@router.post(
    "/verify",
    response_model=TokenVerifyOut,
    responses={
        400: {"description": "Token ausente ou mal-formado"},
        401: {"description": "Token inválido ou expirado"},
        404: {"description": "Cliente não encontrado ou inativo"},
    },
)
def verify_token(body: TokenVerifyIn, db: Session = Depends(get_db)):
    # 1) Verificar presença
    if not body.token:
        raise HTTPException(400, "Token ausente")

    # 2) Decodificar
    try:
        payload = verify_jwt(body.token)
    except ValueError as e:
        raise HTTPException(401, str(e))

    # 3) Pegar CPF do payload
    cpf_value = payload.get("cpf")
    if not cpf_value:
        raise HTTPException(400, "Token não contém CPF")

    # 4) Consultar no repositório
    repo = CustomerRepository(db)
    customer = repo.find_by_cpf(CPF(cpf_value).value)
    if not customer or not customer.active:
        raise HTTPException(404, "Cliente não encontrado ou inativo")

    # 5) OK
    return TokenVerifyOut(
        id=customer.id,
        name=customer.name,
        cpf=customer.cpf.formatted(),
        email=customer.email.value,
    )
