from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

from app.models.transaction import TransactionType, TransactionCategory


class TransactionResponse(BaseModel):
    """
    Schema de resposta de transação individual.
    """
    id: int = Field(..., description="ID da transação")
    user_id: int = Field(..., description="ID do usuário")
    type: TransactionType = Field(..., description="Tipo (income/expense)")
    category: TransactionCategory = Field(..., description="Categoria")
    amount: float = Field(..., description="Valor")
    description: Optional[str] = Field(None, description="Descrição")
    date: datetime = Field(..., description="Data da transação")
    is_recurring: bool = Field(..., description="Se é recorrente")
    created_at: datetime = Field(..., description="Data de criação")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": 1,
                "type": "expense",
                "category": "food",
                "amount": 150.50,
                "description": "Almoço no restaurante",
                "date": "2025-10-30T12:30:00",
                "is_recurring": False,
                "created_at": "2025-10-30T12:30:00"
            }
        }


class TransactionListResponse(BaseModel):
    """
    Schema de resposta para lista de transações.
    """
    transactions: list[TransactionResponse] = Field(..., description="Lista de transações")
    total: int = Field(..., description="Total de transações")
    total_income: float = Field(..., description="Total de receitas")
    total_expense: float = Field(..., description="Total de despesas")
    balance: float = Field(..., description="Saldo (receitas - despesas)")

    class Config:
        json_schema_extra = {
            "example": {
                "transactions": [
                    {
                        "id": 1,
                        "user_id": 1,
                        "type": "income",
                        "category": "salary",
                        "amount": 5000.00,
                        "description": "Salário mensal",
                        "date": "2025-10-05T00:00:00",
                        "is_recurring": True,
                        "created_at": "2025-10-05T00:00:00"
                    }
                ],
                "total": 1,
                "total_income": 5000.00,
                "total_expense": 0.00,
                "balance": 5000.00
            }
        }


class TransactionSummary(BaseModel):
    """
    Schema de resumo financeiro.
    """
    period_start: datetime = Field(..., description="Início do período")
    period_end: datetime = Field(..., description="Fim do período")
    total_income: float = Field(..., description="Total de receitas")
    total_expense: float = Field(..., description="Total de despesas")
    balance: float = Field(..., description="Saldo do período")
    transaction_count: int = Field(..., description="Quantidade de transações")
    

    income_by_category: dict[str, float] = Field(..., description="Receitas por categoria")
    expense_by_category: dict[str, float] = Field(..., description="Despesas por categoria")

    class Config:
        json_schema_extra = {
            "example": {
                "period_start": "2025-10-01T00:00:00",
                "period_end": "2025-10-31T23:59:59",
                "total_income": 5000.00,
                "total_expense": 3500.00,
                "balance": 1500.00,
                "transaction_count": 25,
                "income_by_category": {
                    "salary": 5000.00
                },
                "expense_by_category": {
                    "food": 800.00,
                    "transport": 300.00,
                    "housing": 1500.00,
                    "utilities": 400.00,
                    "entertainment": 500.00
                }
            }
        }
