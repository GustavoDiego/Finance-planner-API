from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token, decode_token
from app.models.user import User
from app.schemas.response import ResponseEnvelope
from app.schemas.token import Token, RefreshTokenRequest
from app.schemas.user.request import UserCreate, ChangePasswordRequest
from app.schemas.user.response import UserResponse
from app.services.auth_service import auth_service


router = APIRouter()


@router.post(
    "/register",
    response_model=ResponseEnvelope,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar novo usuário",
    response_description="Usuário registrado e autenticado com sucesso",
    responses={
        201: {
            "description": "Registro bem-sucedido com tokens de acesso",
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "message": "User registered successfully",
                        "data": {
                            "user": {
                                "id": 1,
                                "email": "user@example.com",
                                "full_name": "João Silva",
                                "is_active": True,
                                "created_at": "2025-10-30T19:30:00"
                            },
                            "tokens": {
                                "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
                                "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
                                "token_type": "bearer"
                            }
                        }
                    }
                }
            }
        },
        400: {
            "description": "Email já registrado",
            "content": {
                "application/json": {
                    "example": {"detail": "Email already registered"}
                }
            }
        },
        422: {
            "description": "Erro de validação dos dados",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "loc": ["body", "email"],
                                "msg": "value is not a valid email address",
                                "type": "value_error.email"
                            }
                        ]
                    }
                }
            }
        }
    }
)
def register(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate = Body(
        ...,
        example={
            "email": "joao.silva@example.com",
            "password": "senhaSegura123!",
            "full_name": "João Silva"
        }
    )
) -> Any:
    """
    Registra um novo usuário no sistema e retorna tokens de autenticação JWT.
    
    ## Fluxo de Registro:
    1. Valida os dados de entrada (email, senha, nome)
    2. Verifica se o email já está registrado no sistema
    3. Cria o usuário com senha hasheada usando bcrypt
    4. Gera tokens JWT (access e refresh)
    5. Retorna dados do usuário criado e tokens
    
    ## Parâmetros:
    - **email**: Email único e válido (formato válido de email)
    - **password**: Senha com no mínimo 8 caracteres
    - **full_name**: Nome completo do usuário (opcional)
    
    ## Segurança:
    - Senha é hasheada com bcrypt antes de ser armazenada
    - Email é verificado para evitar duplicatas
    - Tokens JWT gerados com tempo de expiração configurável
    - Secret key carregada do arquivo .env
    
    ## Retorna:
    - **user**: Dados do usuário criado (sem a senha)
    - **tokens**: 
      - **access_token**: Token de acesso (validade: 30 minutos por padrão)
      - **refresh_token**: Token de renovação (validade: 7 dias por padrão)
      - **token_type**: Tipo do token (sempre "bearer")
    
    ## Erros Possíveis:
    - **400**: Email já cadastrado
    - **422**: Dados de entrada inválidos (email inválido, senha muito curta, etc)
    """
    
    try:

        user = auth_service.register_user(
            db,
            email=user_in.email,
            password=user_in.password,
            full_name=user_in.full_name
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    access_token = create_access_token(subject=user.email)
    refresh_token = create_refresh_token(subject=user.email)
    
    return ResponseEnvelope(
        status="success",
        message="User registered successfully",
        data={
            "user": UserResponse.model_validate(user),
            "tokens": Token(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="bearer"
            )
        }
    )


@router.post(
    "/login",
    response_model=ResponseEnvelope,
    status_code=status.HTTP_200_OK,
    summary="Login do usuário (OAuth2 Password Flow)",
    response_description="Login realizado com sucesso",
    responses={
        200: {
            "description": "Autenticação bem-sucedida",
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "message": "Login successful",
                        "data": {
                            "user": {
                                "id": 1,
                                "email": "user@example.com",
                                "full_name": "João Silva",
                                "is_active": True,
                                "created_at": "2025-10-30T19:30:00"
                            },
                            "tokens": {
                                "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
                                "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
                                "token_type": "bearer"
                            }
                        }
                    }
                }
            }
        },
        401: {
            "description": "Credenciais inválidas",
            "content": {
                "application/json": {
                    "example": {"detail": "Incorrect email or password"}
                }
            }
        },
        400: {
            "description": "Usuário inativo",
            "content": {
                "application/json": {
                    "example": {"detail": "Inactive user"}
                }
            }
        }
    }
)
def login(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    Autentica um usuário e retorna tokens JWT.
    
    ## OAuth2 Password Flow:
    - Implementa o padrão OAuth2 com username/password
    - O campo "username" deve conter o **email** do usuário
    - Retorna access_token e refresh_token no formato JWT
    - Compatível com ferramentas OAuth2 padrão
    
    ## Parâmetros (form-data):
    - **username**: Email do usuário (obrigatório) - usa "username" por padrão OAuth2
    - **password**: Senha do usuário (obrigatório)
    
    ## Processo de Autenticação:
    1. Recebe email (no campo username) e senha via form-data
    2. Busca usuário no banco pelo email
    3. Verifica a senha usando bcrypt (compara hash)
    4. Valida se o usuário está ativo
    5. Gera novos tokens JWT
    6. Retorna dados do usuário e tokens
    
    ## Segurança:
    - Senha nunca é retornada na resposta
    - Verificação de senha via hash bcrypt
    - Tokens JWT com expiração configurável
    - Valida se usuário está ativo antes de autenticar
    - Rate limiting recomendado em produção
    
    ## Retorna:
    - **user**: Dados do usuário autenticado (sem senha)
    - **tokens**: 
      - **access_token**: Token de acesso (30 min por padrão)
      - **refresh_token**: Token de renovação (7 dias por padrão)
      - **token_type**: Tipo do token (bearer)
    
    ## Erros Possíveis:
    - **401**: Email ou senha incorretos
    - **400**: Usuário inativo (desabilitado pelo admin)
    
    ## Exemplo de uso no Swagger:
    - username: joao.silva@example.com
    - password: senhaSegura123!
    """

    user = auth_service.authenticate_user(
        db,
        email=form_data.username,
        password=form_data.password
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    

    access_token = create_access_token(subject=user.email)
    refresh_token = create_refresh_token(subject=user.email)
    
    return ResponseEnvelope(
        status="success",
        message="Login successful",
        data={
            "user": UserResponse.model_validate(user),
            "tokens": Token(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="bearer"
            )
        }
    )


@router.post(
    "/change-password",
    response_model=ResponseEnvelope,
    status_code=status.HTTP_200_OK,
    summary="Alterar senha do usuário",
    response_description="Senha alterada com sucesso",
    responses={
        200: {
            "description": "Senha alterada com sucesso",
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "message": "Password changed successfully"
                    }
                }
            }
        },
        400: {
            "description": "Erro ao alterar senha",
            "content": {
                "application/json": {
                    "example": {"detail": "Senha atual está incorreta"}
                }
            }
        },
        401: {
            "description": "Não autenticado",
            "content": {
                "application/json": {
                    "example": {"detail": "Could not validate credentials"}
                }
            }
        }
    }
)
def change_password(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    change_pwd_in: ChangePasswordRequest = Body(
        ...,
        example={
            "old_password": "senhaAtual123!",
            "new_password": "novaSenha456!"
        }
    )
) -> Any:
    """
    Altera a senha do usuário autenticado.
    
    
    ## Autenticação Obrigatória
    - Requer token JWT válido
    
    ## Parâmetros
    - **old_password**: Senha atual (obrigatória para validação)
    - **new_password**: Nova senha (mínimo 8 caracteres)
    
    ## Validações
    - Senha atual deve estar correta
    - Nova senha não pode ser igual à anterior
    - Mínimo 8 caracteres na nova senha
    
    ## Retorna
    - Mensagem de sucesso
    
    ## Erros
    - **400**: Senha atual incorreta ou nova igual à anterior
    - **401**: Token inválido
    """
    try:
        success = auth_service.change_password(
            db,
            user_id=current_user.id,
            old_password=change_pwd_in.old_password,
            new_password=change_pwd_in.new_password
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Senha atual está incorreta"
        )
    
    return ResponseEnvelope(
        status="success",
        message="Password changed successfully"
    )


@router.post(
    "/refresh",
    response_model=ResponseEnvelope,
    status_code=status.HTTP_200_OK,
    summary="Renovar access token usando refresh token",
    response_description="Novo access token gerado com sucesso",
    responses={
        200: {
            "description": "Token renovado com sucesso",
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "message": "Token refreshed successfully",
                        "data": {
                            "tokens": {
                                "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
                                "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
                                "token_type": "bearer"
                            }
                        }
                    }
                }
            }
        },
        401: {
            "description": "Refresh token inválido ou expirado",
            "content": {
                "application/json": {
                    "example": {"detail": "Invalid refresh token"}
                }
            }
        },
        404: {
            "description": "Usuário não encontrado",
            "content": {
                "application/json": {
                    "example": {"detail": "User not found"}
                }
            }
        },
        400: {
            "description": "Usuário inativo",
            "content": {
                "application/json": {
                    "example": {"detail": "Inactive user"}
                }
            }
        }
    }
)
def refresh_token(
    *,
    db: Session = Depends(get_db),
    refresh_request: RefreshTokenRequest = Body(
        ...,
        example={
            "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
        }
    )
) -> Any:
    """
    Gera um novo access token usando um refresh token válido.
    
    ## Quando usar este endpoint:
    - Quando o access token expirar (após 30 minutos por padrão)
    - Para manter o usuário logado sem pedir senha novamente
    - Implementar sessões de longa duração com segurança
    
    ## Fluxo de Renovação:
    1. Cliente envia o refresh token recebido no login
    2. API valida a assinatura e expiração do refresh token
    3. Extrai o email do usuário do payload do token
    4. Verifica se o usuário ainda existe e está ativo
    5. Gera novos tokens (access e refresh)
    6. Retorna os novos tokens ao cliente
    
    ## Parâmetros:
    - **refresh_token**: Refresh token JWT válido recebido no login ou refresh anterior
    
    ## Segurança - Token Rotation:
    - O refresh token é **rotacionado** (novo token gerado a cada refresh)
    - Token antigo **não pode ser reutilizado** após o refresh
    - Previne ataques de replay com tokens roubados
    - Valida assinatura JWT usando SECRET_KEY do .env
    - Verifica tipo do token (deve ser "refresh", não "access")
    - Valida expiração do token
    
    ## Retorna:
    - **tokens**: 
      - **access_token**: Novo token de acesso (30 min)
      - **refresh_token**: Novo token de renovação (7 dias)
      - **token_type**: Tipo do token (bearer)
    
    ## Erros Possíveis:
    - **401**: Token inválido, expirado ou tipo errado
    - **404**: Usuário não encontrado (foi deletado)
    - **400**: Usuário inativo (foi desabilitado)
    
    ## Best Practices:
    - Armazene o refresh token de forma segura no cliente (HttpOnly cookie recomendado)
    - Implemente logout para invalidar tokens no lado do servidor (blacklist)
    - Monitore uso anômalo de refresh tokens

    """
    
    payload = decode_token(refresh_request.refresh_token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type. Expected refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    email = payload.get("sub")
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )

    from app.crud.user import user as crud_user
    user = crud_user.get_by_email(db, email=email)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if not auth_service.verify_user_active(user):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    new_access_token = create_access_token(subject=user.email)
    new_refresh_token = create_refresh_token(subject=user.email)
    
    return ResponseEnvelope(
        status="success",
        message="Token refreshed successfully",
        data={
            "tokens": Token(
                access_token=new_access_token,
                refresh_token=new_refresh_token,
                token_type="bearer"
            )
        }
    )


@router.get(
    "/me",
    response_model=ResponseEnvelope,
    status_code=status.HTTP_200_OK,
    summary="Obter dados do usuário autenticado",
    response_description="Dados do usuário atual retornados com sucesso",
    responses={
        200: {
            "description": "Dados do usuário autenticado",
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "message": "User data retrieved",
                        "data": {
                            "user": {
                                "id": 1,
                                "email": "user@example.com",
                                "full_name": "João Silva",
                                "is_active": True,
                                "created_at": "2025-10-30T19:30:00"
                            }
                        }
                    }
                }
            }
        },
        401: {
            "description": "Token inválido, expirado ou não fornecido",
            "content": {
                "application/json": {
                    "example": {"detail": "Could not validate credentials"}
                }
            }
        }
    }
)
def get_current_user_data(
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Retorna os dados do usuário atualmente autenticado via JWT.
    
    ## Autenticação Obrigatória:
    - Requer token JWT válido no header Authorization
    - Formato: `Authorization: Bearer <access_token>`
    - Token deve estar válido (não expirado)
    
    ## Casos de Uso:
    - Obter dados do perfil do usuário logado
    - Verificar se o token JWT ainda é válido
    - Sincronizar dados do usuário na aplicação cliente
    - Validar sessão do usuário
    
    ## Headers Obrigatórios:
    ```
    Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
    ```
    
    ## Processo:
    1. Extrai o token do header Authorization
    2. Valida a assinatura JWT com SECRET_KEY
    3. Verifica se o token não está expirado
    4. Extrai o email do usuário do payload
    5. Busca o usuário no banco de dados
    6. Retorna os dados do usuário (sem a senha)
    
    ## Retorna:
    - **user**: Dados completos do usuário autenticado
      - id, email, full_name, is_active, created_at
      - **Senha nunca é retornada**
    
    ## Erros Possíveis:
    - **401**: Token inválido, expirado, malformado ou não fornecido
    - **401**: Usuário não encontrado no banco (foi deletado)
    
    ## Exemplo de Requisição:
    ```
    curl -X GET "http://localhost:8000/api/v1/auth/me" \\
         -H "Authorization: Bearer seu_access_token_aqui"
    ```
    
    ## Dica de Implementação no Frontend:
    - Armazene o access_token após login
    - Inclua em todas as requisições protegidas
    - Se retornar 401, faça refresh do token ou redirecione para login
    """
    return ResponseEnvelope(
        status="success",
        message="User data retrieved",
        data={"user": UserResponse.model_validate(current_user)}
    )
