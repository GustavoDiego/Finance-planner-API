from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError

from app.core.config import settings
from app.core.security import decode_token
from app.crud.user import user as crud_user
from app.db.session import SessionLocal
from app.models.user import User


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_db() -> Generator[Session, None, None]:
    """
    Dependency para obter sessão do banco de dados.
    
    Yields:
        Session: Sessão SQLAlchemy do banco de dados
    
    Usage:
        ```
        @router.get("/users")
        def get_users(db: Session = Depends(get_db)):
            users = crud_user.get_multi(db)
            return users
        ```
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    """
    Dependency para obter usuário autenticado via JWT token.
    
    Valida o token JWT e retorna o usuário associado.
    
    Args:
        db: Sessão do banco de dados
        token: JWT token do header Authorization
    
    Returns:
        User: Usuário autenticado
    
    Raises:
        HTTPException 401: Se token inválido ou usuário não encontrado
    
    Usage:
        ```
        @router.get("/users/me")
        def get_me(current_user: User = Depends(get_current_user)):
            return current_user
        ```
    """

    payload = decode_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    email: Optional[str] = payload.get("sub")
    
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    

    user = crud_user.get_by_email(db, email=email)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Dependency para obter usuário autenticado E ATIVO.
    
    Verifica se o usuário está ativo (is_active = True).
    Usado na maioria dos endpoints protegidos.
    
    Args:
        current_user: Usuário autenticado de get_current_user
    
    Returns:
        User: Usuário autenticado e ativo
    
    Raises:
        HTTPException 400: Se usuário inativo
    
    Usage:
        ```
        @router.get("/transactions")
        def get_transactions(current_user: User = Depends(get_current_active_user)):
            # Usuário está autenticado e ativo
            return current_user.transactions
        ```
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )
    
    return current_user


def get_current_superuser(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """
    Dependency para obter usuário autenticado E ADMIN.
    
    Verifica se o usuário é superusuário (is_superuser = True).
    Usado apenas em endpoints administrativos.
    
    Args:
        current_user: Usuário autenticado e ativo
    
    Returns:
        User: Usuário superusuário
    
    Raises:
        HTTPException 403: Se usuário não é admin
    
    Usage:
        ```
        @router.get("/users")
        def list_all_users(current_user: User = Depends(get_current_superuser)):
            # Apenas admins podem acessar
            ...
        ```
    """

    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    return current_user
