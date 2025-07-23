from sqlalchemy import Column, Integer, String, Boolean
from app.shared.mixins.timestamp_mixin import TimestampMixin
from database import Base


class CustomerModel(TimestampMixin, Base):
    """
    Persisti CPF somente com dígitos (sem máscara)
    """
    __tablename__ = "customers"

    id          = Column(Integer, primary_key=True)
    name        = Column(String,  nullable=False)
    cpf         = Column(String(11), unique=True, nullable=False)
    email       = Column(String,  unique=True, nullable=False)
    active      = Column(Boolean, default=True, nullable=False)

    def __repr__(self):
        return f"<Customer(id={self.id}, cpf={self.cpf})>"