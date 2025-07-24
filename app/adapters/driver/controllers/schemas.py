from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, constr

CPF_PATTERN = r"^\d{3}\.?\d{3}\.?\d{3}\-?\d{2}$"


class CustomerIn(BaseModel):
    """Payload para criação de cliente."""

    name: str = Field(min_length=2, max_length=150)
    cpf: constr(pattern=CPF_PATTERN)
    email: EmailStr


class CustomerUpdateIn(BaseModel):
    """Campos opcionais para atualização."""

    name: Optional[str] = Field(None, min_length=2, max_length=150)
    cpf: Optional[constr(pattern=CPF_PATTERN)] = None
    email: Optional[EmailStr] = None
    active: Optional[bool] = None


class CustomerOut(BaseModel):
    id: int
    name: str
    cpf: str  # sempre formatado
    email: EmailStr
    active: bool


class CustomersOut(CustomerOut):
    created_at: Optional[datetime]
    updated_at: Optional[datetime]


class CustomerIdentifyOut(BaseModel):
    jwt: str


class TokenVerifyIn(BaseModel):
    token: str


class TokenVerifyOut(BaseModel):
    id: int
    name: str
    cpf: str
    email: EmailStr
