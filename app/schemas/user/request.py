from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class UserCreate(BaseModel):
    """Schema para criação de usuário"""
    email: EmailStr = Field(..., description="Email válido e único do usuário")
    password: str = Field(..., min_length=8, description="Senha com no mínimo 8 caracteres")
    full_name: Optional[str] = Field(None, description="Nome completo do usuário")


class UserUpdate(BaseModel):
    """Schema para atualização de usuário"""
    email: Optional[EmailStr] = Field(None, description="Novo email do usuário")
    password: Optional[str] = Field(None, min_length=8, description="Nova senha")
    full_name: Optional[str] = Field(None, description="Novo nome completo")
    is_active: Optional[bool] = Field(None, description="Status ativo/inativo")


class UserLogin(BaseModel):
    """Schema para login"""
    email: EmailStr = Field(..., description="Email do usuário")
    password: str = Field(..., description="Senha do usuário")
