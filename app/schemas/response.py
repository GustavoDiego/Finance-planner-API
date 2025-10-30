from pydantic import BaseModel, Field
from typing import Optional, Any


class ResponseEnvelope(BaseModel):
    """
    Envelope padrão para todas as respostas da API.
    
    Este modelo garante consistência nas respostas em toda a aplicação,
    facilitando o tratamento no lado do cliente.
    
    Attributes:
        status: Indica sucesso ou erro da operação ('success' ou 'error')
        message: Mensagem descritiva sobre a operação realizada
        data: Dados retornados pela operação (pode ser qualquer tipo)
    
    Examples:
        Sucesso:
        ```
        {
            "status": "success",
            "message": "User created successfully",
            "data": {"user": {...}}
        }
        ```
        
        Erro:
        ```
        {
            "status": "error",
            "message": "Validation error",
            "data": null
        }
        ```
    """
    status: str = Field(
        ..., 
        description="Status da operação: 'success' para sucesso ou 'error' para erro",
        example="success"
    )
    message: Optional[str] = Field(
        None, 
        description="Mensagem descritiva sobre o resultado da operação",
        example="Operation completed successfully"
    )
    data: Optional[Any] = Field(
        None, 
        description="Dados retornados pela operação (formato varia por endpoint)",
        example={"user": {"id": 1, "email": "user@example.com"}}
    )

    class Config:
        """Configuração do modelo Pydantic"""
        json_schema_extra = {
            "examples": [
                {
                    "status": "success",
                    "message": "Data retrieved successfully",
                    "data": {
                        "items": [
                            {"id": 1, "name": "Item 1"},
                            {"id": 2, "name": "Item 2"}
                        ],
                        "total": 2
                    }
                },
                {
                    "status": "error",
                    "message": "Resource not found",
                    "data": None
                }
            ]
        }
