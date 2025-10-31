from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ReportPeriodRequest(BaseModel):
    """Schema para requisição de relatório por período."""
    date_from: Optional[datetime] = Field(None, description="Data inicial")
    date_to: Optional[datetime] = Field(None, description="Data final")
    category: Optional[str] = Field(None, description="Filtrar por categoria")

    class Config:
        json_schema_extra = {
            "example": {
                "date_from": "2025-10-01T00:00:00",
                "date_to": "2025-10-31T23:59:59",
                "category": "food"
            }
        }


class MonthlyReportRequest(BaseModel):
    """Schema para relatório mensal."""
    year: int = Field(..., ge=2000, le=2100, description="Ano")
    month: int = Field(..., ge=1, le=12, description="Mês (1-12)")

    class Config:
        json_schema_extra = {
            "example": {
                "year": 2025,
                "month": 10
            }
        }


class YearlyReportRequest(BaseModel):
    """Schema para relatório anual."""
    year: int = Field(..., ge=2000, le=2100, description="Ano")

    class Config:
        json_schema_extra = {
            "example": {
                "year": 2025
            }
        }
