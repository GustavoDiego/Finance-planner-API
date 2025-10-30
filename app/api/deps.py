from typing import Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import decode_token
from app.crud.user import user as crud_user
from app.db.session import SessionLocal
from app.models.user import User
from app.schemas.token import TokenPayload


# OAuth2 scheme para extrair o token do header Authorization
# tokenUrl aponta para o endpoint de login
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login",
    scheme_name="JWT"
)


def get_db() -> Generator:
    """
    Dependência para obter sessão do banco de dados SQLAlchemy.
    
    Cria uma nova sessão do banco de dados para cada requisição HTTP
    e garante que ela seja fechada corretamente após o uso, mesmo em caso de erro.
    
    Esta é uma dependência fundamental usada em praticamente todos os endpoints
    que precisam acessar o banco de dados.
    
    Yields:
        Session: Sessão ativa do SQLAlchemy para operações no banco
    
    Usage:
        ```
        @router.get("/users/{user_id}")
        def get_user(user_id: int, db: Session = Depends(get_db)):
            return db.query(User).filter(User.id == user_id).first()
        ```
    
    Notes:
        - Cada requisição recebe uma sessão independente
        - A sessão é fechada automaticamente no finally
        - Previne vazamento de conexões com o banco
        - Thread-safe para requisições concorrentes
    
    See Also:
        - app/db/session.py: Configuração do SessionLocal
        - SQLAlchemy docs: https://docs.sqlalchemy.org/en/14/orm/session.html
    """
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    """
    Dependência para obter o usuário atual autenticado via token JWT.
    
    Esta é a dependência principal de autenticação. Ela:
    1. Extrai o token JWT do header Authorization
    2. Valida a assinatura usando SECRET_KEY
    3. Verifica se o token não expirou
    4. Extrai o email do usuário do payload
    5. Busca o usuário no banco de dados
    6. Retorna o objeto User completo
    
    Args:
        db: Sessão do banco de dados (injetada automaticamente)
        token: Token JWT extraído do header Authorization (injetado pelo oauth2_scheme)
    
    Returns:
        User: Objeto do usuário autenticado com todos os dados
    
    Raises:
        HTTPException 401: Se token for inválido, expirado ou usuário não existir
            - Token malformado ou com assinatura inválida
            - Token expirado
            - Usuário não encontrado no banco (foi deletado)
            - Payload do token inválido
    
    Usage:
        ```
        @router.get("/protected")
        def protected_route(current_user: User = Depends(get_current_user)):
            return {"user_id": current_user.id, "email": current_user.email}
        ```
    
    Security:
        - Valida assinatura JWT com SECRET_KEY do .env
        - Verifica expiração do token automaticamente
        - Não aceita tokens de tipo incorreto
        - Retorna 401 com header WWW-Authenticate para clientes OAuth2
    
    Notes:
        - Esta dependência pode ser usada em qualquer endpoint que requer autenticação
        - Não verifica se o usuário está ativo (use get_current_active_user para isso)
        - O token deve estar no formato: "Bearer <token>"
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decodifica o token JWT
        payload = decode_token(token)
        if payload is None:
            raise credentials_exception
        
        # Valida o payload usando o schema Pydantic
        token_data = TokenPayload(**payload)
        
        # Verifica se o subject (email) está presente
        if token_data.sub is None:
            raise credentials_exception
            
    except (JWTError, ValidationError):
        raise credentials_exception
    
    # Busca o usuário no banco pelo email
    user = crud_user.get_by_email(db, email=token_data.sub)
    
    if user is None:
        raise credentials_exception
    
    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependência para garantir que o usuário autenticado está ativo.
    
    Esta dependência adiciona uma camada extra de validação sobre get_current_user,
    verificando se o usuário não foi desabilitado/desativado por um administrador.
    
    Use esta dependência em endpoints que não devem ser acessíveis por
    usuários inativos, mesmo que tenham um token válido.
    
    Args:
        current_user: Usuário autenticado (injetado por get_current_user)
    
    Returns:
        User: Objeto do usuário ativo
    
    Raises:
        HTTPException 400: Se o usuário estiver inativo (is_active=False)
    
    Usage:
        ```
        @router.get("/sensitive-data")
        def get_sensitive_data(
            current_user: User = Depends(get_current_active_user)
        ):
            # Apenas usuários ativos podem acessar
            return {"data": "sensitive"}
        ```
    
    Flow:
        1. get_current_user valida o token e busca o usuário
        2. get_current_active_user verifica se user.is_active == True
        3. Se inativo, retorna erro 400
        4. Se ativo, retorna o usuário
    
    Notes:
        - Esta é a dependência recomendada para a maioria dos endpoints protegidos
        - Usuários inativos mantêm tokens válidos, mas não podem acessar recursos
        - Administradores podem desativar usuários sem invalidar seus tokens
    """
    if not crud_user.is_active(current_user):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


def get_current_superuser(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependência para garantir que o usuário autenticado é um superusuário.
    
    Esta dependência verifica se o usuário tem privilégios de administrador,
    permitindo acesso apenas a usuários com is_superuser=True.
    
    Use em endpoints administrativos que requerem privilégios elevados,
    como gerenciamento de usuários, configurações do sistema, etc.
    
    Args:
        current_user: Usuário autenticado (injetado por get_current_user)
    
    Returns:
        User: Objeto do superusuário com privilégios administrativos
    
    Raises:
        HTTPException 403: Se o usuário não for superusuário
            - Código 403 Forbidden indica falta de permissões
            - Diferente de 401 (não autenticado) ou 400 (inativo)
    
    Usage:
        ```
        @router.delete("/users/{user_id}")
        def delete_user(
            user_id: int,
            current_user: User = Depends(get_current_superuser),
            db: Session = Depends(get_db)
        ):
            # Apenas superusuários podem deletar usuários
            return crud_user.delete(db, id=user_id)
        ```
    
    Security Levels:
        - get_current_user: Qualquer usuário autenticado
        - get_current_active_user: Usuário autenticado + ativo
        - get_current_superuser: Usuário autenticado + ativo + admin
    
    Notes:
        - Não verifica se o usuário está ativo (requer apenas is_superuser=True)
        - Para verificar ambos, combine: `get_current_active_user` + verificação manual
        - Retorna 403 (Forbidden) em vez de 401 (Unauthorized)
        - Use para proteger endpoints críticos e administrativos
    
    Examples:
        Endpoints que devem usar esta dependência:
        - Criar/deletar usuários
        - Modificar permissões
        - Acessar logs do sistema
        - Alterar configurações globais
        - Visualizar dados de todos os usuários
    """
    if not crud_user.is_superuser(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges"
        )
    return current_user
