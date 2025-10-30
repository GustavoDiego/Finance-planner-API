from datetime import datetime, timedelta
from typing import Any, Optional, Union

from jose import jwt, JWTError
from passlib.context import CryptContext

from app.core.config import settings


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica se a senha em texto plano corresponde ao hash armazenado.
    
    Usa bcrypt para comparação segura de senhas.
    
    Args:
        plain_password: Senha em texto plano fornecida pelo usuário
        hashed_password: Hash da senha armazenado no banco de dados
    
    Returns:
        bool: True se a senha corresponde ao hash, False caso contrário
    
    Example:
        ```
        stored_hash = "$2b$12$..."
        user_password = "minhaSenha123"
        is_valid = verify_password(user_password, stored_hash)
        ```
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Gera um hash seguro da senha usando bcrypt.
    
    O hash gerado é único mesmo para senhas idênticas devido ao salt.
    
    Args:
        password: Senha em texto plano a ser hasheada
    
    Returns:
        str: Hash bcrypt da senha (sempre começa com $2b$)
    
    Example:
        ```
        password = "minhaSenha123"
        hashed = get_password_hash(password)
        # Resultado: "$2b$12$kQx8vF..."
        ```
    
    Security:
        - Usa bcrypt com custo padrão de 12 rounds
        - Salt único gerado automaticamente
        - Resistente a ataques de rainbow table
    """
    return pwd_context.hash(password)


def create_access_token(
    subject: Union[str, Any], 
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Cria um token JWT de acesso (curta duração).
    
    O access token é usado para autenticar requisições à API.
    Tem duração curta (30 minutos por padrão) por motivos de segurança.
    
    Args:
        subject: Identificador do usuário (geralmente email ou ID)
        expires_delta: Tempo de expiração customizado (opcional)
    
    Returns:
        str: Token JWT codificado como string
    
    Token Payload:
        - sub: Subject (identificador do usuário)
        - exp: Expiration timestamp
        - Assinado com SECRET_KEY do .env
    
    Example:
        ```
        token = create_access_token(subject="user@example.com")
        # Token válido por 30 minutos
        
        # Com expiração customizada
        custom_expire = timedelta(hours=1)
        token = create_access_token(
            subject="user@example.com",
            expires_delta=custom_expire
        )
        ```
    
    Security:
        - Usa algoritmo HS256 (HMAC com SHA-256)
        - SECRET_KEY deve ser mantida em segredo (.env)
        - Token não pode ser modificado sem invalidar a assinatura
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(
    subject: Union[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Cria um token JWT de refresh (longa duração).
    
    O refresh token é usado para obter novos access tokens sem fazer login novamente.
    Tem duração longa (7 dias por padrão) e inclui campo "type" para diferenciação.
    
    Args:
        subject: Identificador do usuário (geralmente email ou ID)
        expires_delta: Tempo de expiração customizado (opcional)
    
    Returns:
        str: Refresh token JWT codificado como string
    
    Token Payload:
        - sub: Subject (identificador do usuário)
        - exp: Expiration timestamp
        - type: "refresh" (para validação)
        - Assinado com SECRET_KEY do .env
    
    Example:
        ```
        refresh = create_refresh_token(subject="user@example.com")
        # Token válido por 7 dias
        
        # Com expiração customizada
        custom_expire = timedelta(days=30)
        refresh = create_refresh_token(
            subject="user@example.com",
            expires_delta=custom_expire
        )
        ```
    
    Security:
        - Campo "type" previne uso de access token como refresh
        - Deve ser armazenado de forma segura no cliente
        - Considere implementar token rotation em produção
        - Recomenda-se usar HttpOnly cookies
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )
    
    to_encode = {"exp": expire, "sub": str(subject), "type": "refresh"}
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def decode_token(token: str) -> Optional[dict]:
    """
    Decodifica e valida um token JWT.
    
    Verifica a assinatura e a expiração do token.
    Retorna o payload se válido, None se inválido ou expirado.
    
    Args:
        token: Token JWT a ser decodificado (string)
    
    Returns:
        dict: Payload do token se válido, None se inválido ou expirado
            Payload contém: {"sub": "...", "exp": ..., "type": "..."}
    
    Example:
        ```
        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        payload = decode_token(token)
        
        if payload:
            email = payload["sub"]
            token_type = payload.get("type", "access")
            print(f"Token válido para: {email}")
        else:
            print("Token inválido ou expirado")
        ```
    
    Validations:
        - Verifica assinatura usando SECRET_KEY
        - Valida algoritmo (deve ser HS256)
        - Verifica se não está expirado (campo "exp")
        - Retorna None para qualquer erro
    
    Error Handling:
        - Token malformado -> None
        - Assinatura inválida -> None
        - Token expirado -> None
        - Algoritmo incorreto -> None
    
    Security:
        - Sempre valide o payload retornado
        - Verifique o campo "type" se necessário
        - Não confie em tokens não verificados
    """
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:

        return None
