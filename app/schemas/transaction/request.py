from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

from app.models.transaction import TransactionType, TransactionCategory


class TransactionCreate(BaseModel):
    """
    Schema para criação de transação.
    """
    type: TransactionType = Field(..., description="Tipo da transação (income ou expense)")
    category: TransactionCategory = Field(..., description="Categoria da transação")
    amount: float = Field(..., gt=0, description="Valor da transação (deve ser positivo)")
    description: Optional[str] = Field(None, max_length=500, description="Descrição da transação")
    date: datetime = Field(..., description="Data da transação")
    is_recurring: bool = Field(default=False, description="Se é transação recorrente")

    class Config:
        json_schema_extra = {
            "example": {
                "type": "expense",
                "category": "food",
                "amount": 150.50,
                "description": "Almoço no restaurante",
                "date": "2025-10-30T12:30:00",
                "is_recurring": False
            }
        }


class TransactionUpdate(BaseModel):
    """
    Schema para atualização de transação.
    """
    type: Optional[TransactionType] = Field(None, description="Novo tipo da transação")
    category: Optional[TransactionCategory] = Field(None, description="Nova categoria")
    amount: Optional[float] = Field(None, gt=0, description="Novo valor")
    description: Optional[str] = Field(None, max_length=500, description="Nova descrição")
    date: Optional[datetime] = Field(None, description="Nova data")
    is_recurring: Optional[bool] = Field(None, description="Atualizar recorrência")

    class Config:
        json_schema_extra = {
            "example": {
                "amount": 175.00,
                "description": "Almoço no restaurante (atualizado)"
            }
        }


class TransactionFilter(BaseModel):
    """
    Schema para filtros de busca de transações.
    """
    type: Optional[TransactionType] = Field(None, description="Filtrar por tipo")
    category: Optional[TransactionCategory] = Field(None, description="Filtrar por categoria")
    date_from: Optional[datetime] = Field(None, description="Data inicial")
    date_to: Optional[datetime] = Field(None, description="Data final")
    min_amount: Optional[float] = Field(None, ge=0, description="Valor mínimo")
    max_amount: Optional[float] = Field(None, ge=0, description="Valor máximo")
    is_recurring: Optional[bool] = Field(None, description="Filtrar por recorrência")

    class Config:
        json_schema_extra = {
            "example": {
                "type": "expense",
                "date_from": "2025-10-01T00:00:00",
                "date_to": "2025-10-31T23:59:59",
                "category": "food"
            }
        }
