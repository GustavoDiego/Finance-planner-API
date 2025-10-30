from pydantic import BaseModel, Field
from typing import Optional, Any


class ResponseEnvelope(BaseModel):
    """Envelope padrão para respostas da API"""
    status: str = Field(..., description="Status: 'success' ou 'error'")
    message: Optional[str] = Field(None, description="Mensagem descritiva")
    data: Optional[Any] = Field(None, description="Dados retornados")
