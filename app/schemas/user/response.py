from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


class UserResponse(BaseModel):
    """Schema de resposta básica do usuário."""
    id: int = Field(..., description="ID único do usuário")
    email: EmailStr = Field(..., description="Email do usuário")
    full_name: Optional[str] = Field(None, description="Nome completo")
    is_active: bool = Field(..., description="Status ativo/inativo")
    created_at: datetime = Field(..., description="Data de criação")

    class Config:
        from_attributes = True
