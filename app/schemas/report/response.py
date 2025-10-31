from pydantic import BaseModel, Field
from datetime import datetime
from typing import Dict, List, Optional


class DailyTrendItem(BaseModel):
    """Item da tendência diária."""
    date: str = Field(..., description="Data")
    total: float = Field(..., description="Total do dia")

    class Config:
        json_schema_extra = {
            "example": {
                "date": "2025-10-30",
                "total": 150.50
            }
        }


class RecurringTransactionItem(BaseModel):
    """Item de transação recorrente."""
    id: int = Field(..., description="ID da transação")
    type: str = Field(..., description="Tipo (income/expense)")
    category: str = Field(..., description="Categoria")
    amount: float = Field(..., description="Valor")
    description: Optional[str] = Field(None, description="Descrição")

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "type": "income",
                "category": "salary",
                "amount": 5000.00,
                "description": "Salário mensal"
            }
        }


class RecurringTransactionsReport(BaseModel):
    """Relatório de transações recorrentes."""
    recurring_transactions: List[RecurringTransactionItem]
    monthly_expense_estimate: float
    monthly_income_estimate: float
    monthly_balance_estimate: float

    class Config:
        json_schema_extra = {
            "example": {
                "recurring_transactions": [
                    {
                        "id": 1,
                        "type": "income",
                        "category": "salary",
                        "amount": 5000.00,
                        "description": "Salário mensal"
                    },
                    {
                        "id": 2,
                        "type": "expense",
                        "category": "housing",
                        "amount": 1500.00,
                        "description": "Aluguel"
                    }
                ],
                "monthly_expense_estimate": 2500.00,
                "monthly_income_estimate": 5000.00,
                "monthly_balance_estimate": 2500.00
            }
        }


class HighestExpensesReport(BaseModel):
    """Relatório das maiores despesas."""
    date_range: str = Field(..., description="Período")
    highest_expenses: List[Dict] = Field(..., description="Top 10 despesas")
    total: float = Field(..., description="Total das despesas listadas")

    class Config:
        json_schema_extra = {
            "example": {
                "date_range": "Últimos 30 dias",
                "highest_expenses": [
                    {
                        "id": 1,
                        "category": "housing",
                        "amount": 1500.00,
                        "description": "Aluguel",
                        "date": "2025-10-01T00:00:00"
                    }
                ],
                "total": 1500.00
            }
        }


class MonthlyBreakdownItem(BaseModel):
    """Item do breakdown mensal."""
    month: str = Field(..., description="Mês")
    total_income: float = Field(..., description="Total de receitas")
    total_expense: float = Field(..., description="Total de despesas")
    balance: float = Field(..., description="Saldo do mês")

    class Config:
        json_schema_extra = {
            "example": {
                "month": "January",
                "total_income": 5000.00,
                "total_expense": 2500.00,
                "balance": 2500.00
            }
        }


class YearlyBreakdownReport(BaseModel):
    """Relatório de breakdown anual."""
    year: int = Field(..., description="Ano")
    monthly_breakdown: List[MonthlyBreakdownItem]
    yearly_total_income: float
    yearly_total_expense: float
    yearly_balance: float

    class Config:
        json_schema_extra = {
            "example": {
                "year": 2025,
                "monthly_breakdown": [
                    {
                        "month": "January",
                        "total_income": 5000.00,
                        "total_expense": 2500.00,
                        "balance": 2500.00
                    }
                ],
                "yearly_total_income": 60000.00,
                "yearly_total_expense": 30000.00,
                "yearly_balance": 30000.00
            }
        }


class ComprehensiveFinancialReport(BaseModel):
    """Relatório financeiro abrangente."""
    period_start: datetime
    period_end: datetime
    total_income: float
    total_expense: float
    balance: float
    transaction_count: int
    income_by_category: Dict[str, float]
    expense_by_category: Dict[str, float]
    highest_expenses: List[Dict]
    spending_trend: List[DailyTrendItem]
    is_in_deficit: bool
    recurring_summary: RecurringTransactionsReport

    class Config:
        json_schema_extra = {
            "example": {
                "period_start": "2025-10-01T00:00:00",
                "period_end": "2025-10-31T23:59:59",
                "total_income": 5000.00,
                "total_expense": 2500.00,
                "balance": 2500.00,
                "transaction_count": 15,
                "income_by_category": {"salary": 5000.00},
                "expense_by_category": {"food": 800.00, "transport": 300.00},
                "highest_expenses": [],
                "spending_trend": [],
                "is_in_deficit": False,
                "recurring_summary": {}
            }
        }
