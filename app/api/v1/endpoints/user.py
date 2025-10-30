from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_active_user, get_current_superuser
from app.crud.user import user as crud_user
from app.models.user import User
from app.schemas.user.request import UserCreate, UserUpdate
from app.schemas.user.response import UserResponse
from app.schemas.response import ResponseEnvelope

router = APIRouter()


@router.post(
    "/",
    response_model=ResponseEnvelope,
    status_code=status.HTTP_201_CREATED,
    summary="Criar novo usuário (Admin)",
    response_description="Usuário criado com sucesso pelo administrador",
    dependencies=[Depends(get_current_superuser)], 
    responses={
        201: {
            "description": "Usuário criado com sucesso",
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "message": "User created successfully",
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
        400: {
            "description": "Email já registrado",
            "content": {
                "application/json": {
                    "example": {"detail": "Email already registered"}
                }
            }
        },
        403: {
            "description": "Usuário não tem privilégios de administrador",
            "content": {
                "application/json": {
                    "example": {"detail": "The user doesn't have enough privileges"}
                }
            }
        }
    }
)
def create_user(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate,
    current_user: User = Depends(get_current_superuser)
) -> Any:
    """
    Cria um novo usuário no sistema (apenas administradores).
    
    ## Autenticação Obrigatória:
    - Requer token JWT válido de um superusuário
    - Apenas administradores podem criar usuários por este endpoint
    - Para registro público, use `/auth/register`
    
    ## Diferença entre endpoints:
    - **POST /auth/register**: Registro público (qualquer pessoa)
    - **POST /users/**: Criação por admin (requer autenticação de superusuário)
    
    ## Parâmetros:
    - **email**: Email único e válido do usuário (obrigatório)
    - **password**: Senha com no mínimo 8 caracteres (obrigatório)
    - **full_name**: Nome completo do usuário (opcional)
    
    ## Validações:
    - Verifica se o email já está registrado
    - Valida formato do email
    - Valida comprimento mínimo da senha
    - Hash seguro da senha antes de salvar (bcrypt)
    
    ## Retorna:
    - Dados do usuário criado (sem a senha)
    - Status HTTP 201 Created
    
    ## Erros:
    - **400**: Email já registrado
    - **403**: Usuário não é superusuário
    - **401**: Token inválido ou não fornecido
    
    ## Headers Obrigatórios:
    ```
    Authorization: Bearer <access_token_do_admin>
    ```
    """
    user = crud_user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    user = crud_user.create(db=db, obj_in=user_in)
    
    return ResponseEnvelope(
        status="success",
        message="User created successfully",
        data={"user": UserResponse.model_validate(user)}
    )


@router.get(
    "/{user_id}",
    response_model=ResponseEnvelope,
    status_code=status.HTTP_200_OK,
    summary="Buscar usuário por ID",
    response_description="Usuário encontrado",
    responses={
        200: {
            "description": "Usuário encontrado com sucesso",
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "message": "User found",
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
        403: {
            "description": "Sem permissão para visualizar outro usuário",
            "content": {
                "application/json": {
                    "example": {"detail": "Not enough permissions"}
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
        }
    }
)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Busca um usuário específico pelo ID.
    
    ## Autenticação Obrigatória:
    - Requer token JWT válido
    
    ## Regras de Permissão:
    - Usuários comuns podem ver apenas seus próprios dados
    - Superusuários podem ver dados de qualquer usuário
    
    ## Parâmetros:
    - **user_id**: ID único do usuário a ser buscado
    
    ## Retorna:
    - Dados completos do usuário encontrado (sem senha)
    - Status HTTP 200 OK
    
    ## Erros:
    - **404**: Usuário não encontrado
    - **403**: Tentativa de acessar dados de outro usuário sem ser admin
    - **401**: Token inválido ou não fornecido
    
    ## Headers Obrigatórios:
    ```
    Authorization: Bearer <access_token>
    ```
    
    ## Exemplos de Uso:
    - Usuário comum consultando próprio perfil: GET /users/1 (próprio ID)
    - Admin consultando qualquer usuário: GET /users/5
    """
    user = crud_user.get(db=db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if user.id != current_user.id and not crud_user.is_superuser(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return ResponseEnvelope(
        status="success",
        message="User found",
        data={"user": UserResponse.model_validate(user)}
    )


@router.get(
    "/",
    response_model=ResponseEnvelope,
    status_code=status.HTTP_200_OK,
    summary="Listar todos os usuários (Admin)",
    response_description="Lista de usuários retornada com sucesso",
    dependencies=[Depends(get_current_superuser)],  # Apenas admin
    responses={
        200: {
            "description": "Lista de usuários com paginação",
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "message": "Users retrieved successfully",
                        "data": {
                            "users": [
                                {
                                    "id": 1,
                                    "email": "user1@example.com",
                                    "full_name": "João Silva",
                                    "is_active": True,
                                    "created_at": "2025-10-30T19:30:00"
                                }
                            ],
                            "total": 1,
                            "skip": 0,
                            "limit": 100
                        }
                    }
                }
            }
        },
        403: {
            "description": "Sem privilégios de administrador",
            "content": {
                "application/json": {
                    "example": {"detail": "The user doesn't have enough privileges"}
                }
            }
        }
    }
)
def list_users(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_superuser)
) -> Any:
    """
    Lista todos os usuários do sistema com paginação (apenas administradores).
    
    ## Autenticação Obrigatória:
    - Requer token JWT válido de superusuário
    - Apenas administradores podem listar todos os usuários
    
    ## Parâmetros de Query:
    - **skip**: Número de registros a pular (padrão: 0)
    - **limit**: Número máximo de registros a retornar (padrão: 100, máximo: 100)
    
    ## Paginação:
    - Use `skip` e `limit` para navegar pelos resultados
    - Exemplo: `/users?skip=0&limit=10` retorna os primeiros 10 usuários
    - Para próxima página: `/users?skip=10&limit=10`
    
    ## Retorna:
    - **users**: Lista de usuários (sem senhas)
    - **total**: Total de usuários retornados nesta página
    - **skip**: Offset usado
    - **limit**: Limite usado
    - Status HTTP 200 OK
    
    ## Erros:
    - **403**: Usuário não é superusuário
    - **401**: Token inválido ou não fornecido
    
    ## Headers Obrigatórios:
    ```
    Authorization: Bearer <access_token_do_admin>
    ```
    
    ## Notas:
    - Senhas nunca são retornadas
    - Lista inclui usuários ativos e inativos
    - Útil para painéis administrativos
    """
    users = crud_user.get_multi(db=db, skip=skip, limit=limit)
    total = len(users)
    
    return ResponseEnvelope(
        status="success",
        message="Users retrieved successfully",
        data={
            "users": [UserResponse.model_validate(user) for user in users],
            "total": total,
            "skip": skip,
            "limit": limit
        }
    )


@router.put(
    "/{user_id}",
    response_model=ResponseEnvelope,
    status_code=status.HTTP_200_OK,
    summary="Atualizar usuário",
    response_description="Usuário atualizado com sucesso",
    responses={
        200: {
            "description": "Usuário atualizado com sucesso",
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "message": "User updated successfully",
                        "data": {
                            "user": {
                                "id": 1,
                                "email": "newemail@example.com",
                                "full_name": "João Silva Atualizado",
                                "is_active": True,
                                "created_at": "2025-10-30T19:30:00"
                            }
                        }
                    }
                }
            }
        },
        403: {
            "description": "Sem permissão para atualizar outro usuário",
            "content": {
                "application/json": {
                    "example": {"detail": "Not enough permissions"}
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
        }
    }
)
def update_user(
    user_id: int,
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Atualiza os dados de um usuário.
    
    ## Autenticação Obrigatória:
    - Requer token JWT válido
    
    ## Regras de Permissão:
    - Usuários podem atualizar apenas seus próprios dados
    - Superusuários podem atualizar dados de qualquer usuário
    
    ## Parâmetros:
    - **user_id**: ID do usuário a ser atualizado
    - **email**: Novo email (opcional)
    - **password**: Nova senha (opcional, será hasheada)
    - **full_name**: Novo nome completo (opcional)
    - **is_active**: Novo status ativo/inativo (apenas admin)
    
    ## Validações:
    - Apenas campos enviados são atualizados (PATCH semântico)
    - Email é validado se fornecido
    - Senha é hasheada antes de salvar
    - Campo `is_active` só pode ser alterado por admin
    
    ## Retorna:
    - Dados do usuário atualizado (sem senha)
    - Status HTTP 200 OK
    
    ## Erros:
    - **404**: Usuário não encontrado
    - **403**: Tentativa de atualizar outro usuário sem ser admin
    - **400**: Email já está em uso por outro usuário
    - **401**: Token inválido
    
    ## Headers Obrigatórios:
    ```
    Authorization: Bearer <access_token>
    ```
    
    ## Exemplo de Body (todos os campos são opcionais):
    ```
    {
        "full_name": "Novo Nome",
        "password": "novaSenha123!"
    }
    ```
    """
    user = crud_user.get(db=db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if user.id != current_user.id and not crud_user.is_superuser(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    if not crud_user.is_superuser(current_user) and user_in.is_active is not None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can change user active status"
        )
    
    user = crud_user.update(db=db, db_obj=user, obj_in=user_in)
    
    return ResponseEnvelope(
        status="success",
        message="User updated successfully",
        data={"user": UserResponse.model_validate(user)}
    )


@router.delete(
    "/{user_id}",
    response_model=ResponseEnvelope,
    status_code=status.HTTP_200_OK,
    summary="Deletar usuário (Admin)",
    response_description="Usuário deletado com sucesso",
    dependencies=[Depends(get_current_superuser)],
    responses={
        200: {
            "description": "Usuário deletado com sucesso",
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "message": "User deleted successfully",
                        "data": None
                    }
                }
            }
        },
        403: {
            "description": "Sem privilégios de administrador",
            "content": {
                "application/json": {
                    "example": {"detail": "The user doesn't have enough privileges"}
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
        }
    }
)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
) -> Any:
    """
    Deleta um usuário do sistema (apenas administradores).
    
    ## Autenticação Obrigatória:
    - Requer token JWT válido de superusuário
    - Apenas administradores podem deletar usuários
    
    ## Parâmetros:
    - **user_id**: ID do usuário a ser deletado
    
    ## Atenção:
    - Esta operação é **irreversível**
    - Considere desativar o usuário (is_active=False) ao invés de deletar
    - Dados relacionados podem ser afetados (depende das foreign keys)
    
    ## Retorna:
    - Mensagem de sucesso
    - Status HTTP 200 OK
    
    ## Erros:
    - **404**: Usuário não encontrado
    - **403**: Usuário não é superusuário
    - **401**: Token inválido
    
    ## Headers Obrigatórios:
    ```
    Authorization: Bearer <access_token_do_admin>
    ```
    
    ## Alternativa Recomendada:
    - Use PUT /users/{user_id} com `{"is_active": false}` para desativar
    - Desativar preserva dados históricos e permite reativação
    """
    user = crud_user.get(db=db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user = crud_user.delete(db=db, id=user_id)
    
    return ResponseEnvelope(
        status="success",
        message="User deleted successfully",
        data=None
    )
