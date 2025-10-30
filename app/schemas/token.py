from pydantic import BaseModel, Field
from typing import Optional


class Token(BaseModel):
    """
    Schema de resposta contendo tokens de autenticação JWT.
    
    Retornado após login bem-sucedido ou refresh de token.
    
    Attributes:
        access_token: Token JWT de acesso para autenticação de requisições
        refresh_token: Token JWT de longa duração para renovar access_token
        token_type: Tipo do token (sempre "bearer" para JWT)
    
    Usage:
        ```
        # No cliente, armazenar os tokens
        tokens = response.data["tokens"]
        access_token = tokens["access_token"]
        refresh_token = tokens["refresh_token"]
        
        # Usar em requisições
        headers = {"Authorization": f"Bearer {access_token}"}
        ```
    """
    access_token: str = Field(
        ..., 
        description="Token JWT de acesso (curta duração, geralmente 30 minutos)",
        example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyQGV4YW1wbGUuY29tIiwiZXhwIjoxNjk4Nzg5MDAwfQ.signature"
    )
    refresh_token: str = Field(
        ..., 
        description="Token JWT de renovação (longa duração, geralmente 7 dias)",
        example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyQGV4YW1wbGUuY29tIiwidHlwZSI6InJlZnJlc2giLCJleHAiOjE2OTkzOTM4MDB9.signature"
    )
    token_type: str = Field(
        default="bearer", 
        description="Tipo do token (padrão OAuth2 Bearer)",
        example="bearer"
    )

    class Config:
        """Configuração do modelo Pydantic"""
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }


class TokenPayload(BaseModel):
    """
    Schema do payload decodificado de um token JWT.
    
    Usado internamente para validar e extrair informações do token.
    
    Attributes:
        sub: Subject (identificador do usuário, geralmente email)
        exp: Timestamp Unix de expiração do token
        type: Tipo do token ('access' ou 'refresh')
    
    Notes:
        - Este schema não é retornado pela API
        - Usado apenas para validação interna do token
        - O campo 'sub' contém o email do usuário
    """
    sub: Optional[str] = Field(
        None, 
        description="Subject: identificador do usuário (email)",
        example="user@example.com"
    )
    exp: Optional[int] = Field(
        None, 
        description="Expiration: timestamp Unix de quando o token expira",
        example=1698789000
    )
    type: Optional[str] = Field(
        None, 
        description="Tipo do token: 'access' ou 'refresh'",
        example="access"
    )

    class Config:
        """Configuração do modelo Pydantic"""
        json_schema_extra = {
            "example": {
                "sub": "user@example.com",
                "exp": 1698789000,
                "type": "access"
            }
        }


class RefreshTokenRequest(BaseModel):
    """
    Schema de requisição para renovar um access token.
    
    Enviado no endpoint /auth/refresh para obter novos tokens.
    
    Attributes:
        refresh_token: Refresh token JWT válido recebido no login
    
    Usage:
        ```
        # Exemplo de uso
        request_body = {
            "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        }
        response = requests.post("/auth/refresh", json=request_body)
        ```
    
    Security:
        - O refresh token deve ser armazenado de forma segura no cliente
        - Recomenda-se usar HttpOnly cookies em produção
        - Não compartilhar ou expor o refresh token
    """
    refresh_token: str = Field(
        ..., 
        description="Refresh token JWT válido recebido no login ou refresh anterior",
        min_length=20,
        example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyQGV4YW1wbGUuY29tIiwidHlwZSI6InJlZnJlc2giLCJleHAiOjE2OTkzOTM4MDB9.signature"
    )

    class Config:
        """Configuração do modelo Pydantic"""
        json_schema_extra = {
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyQGV4YW1wbGUuY29tIiwidHlwZSI6InJlZnJlc2giLCJleHAiOjE2OTkzOTM4MDB9..."
            }
        }
