from typing import Optional
from sqlalchemy.orm import Session

from app.crud.user import user as crud_user
from app.core.security import verify_password, get_password_hash
from app.models.user import User
from app.schemas.user.request import UserCreate


class AuthService:
    """
    Serviço de autenticação com regras de negócio.
    
    """
    
    @staticmethod
    def register_user(
        db: Session,
        *,
        email: str,
        password: str,
        full_name: Optional[str] = None
    ) -> User:
        """
        Registra um novo usuário com validações de negócio.
        
        
        Args:
            db: Sessão do banco
            email: Email do usuário
            password: Senha em texto plano
            full_name: Nome completo (opcional)
        
        Returns:
            User criado
        
        Raises:
            ValueError: Se email já está registrado
        """

        existing = crud_user.get_by_email(db, email=email)
        if existing:
            raise ValueError(f"Email {email} já está registrado")

        user_in = UserCreate(
            email=email,
            password=password,
            full_name=full_name
        )
        return crud_user.create(db, obj_in=user_in)
    
    @staticmethod
    def authenticate_user(
        db: Session,
        *,
        email: str,
        password: str
    ) -> Optional[User]:
        """
        Autentica um usuário com email e senha.
        
        
        Args:
            db: Sessão do banco
            email: Email do usuário
            password: Senha em texto plano
        
        Returns:
            User se autenticado, None caso contrário
        """

        user = crud_user.get_by_email(db, email=email)
        if not user:
            return None

        if not verify_password(password, user.hashed_password):
            return None
        

        if not user.is_active:
            return None
        
        return user
    
    @staticmethod
    def verify_user_active(user: User) -> bool:
        """
        Verifica se um usuário está ativo.
        

        
        Args:
            user: Objeto User
        
        Returns:
            True se ativo, False caso contrário
        """
        return user.is_active
    
    @staticmethod
    def verify_user_superuser(user: User) -> bool:
        """
        Verifica se um usuário é superusuário.
        
        
        Args:
            user: Objeto User
        
        Returns:
            True se é admin, False caso contrário
        """
        return user.is_superuser
    
    @staticmethod
    def verify_user_credentials(
        db: Session,
        *,
        user_id: int,
        password: str
    ) -> bool:
        """
        Verifica se a senha está correta para um usuário.
        
        
        Args:
            db: Sessão do banco
            user_id: ID do usuário
            password: Senha em texto plano
        
        Returns:
            True se senha está correta, False caso contrário
        """
        user = crud_user.get(db, id=user_id)
        if not user:
            return False
        return verify_password(password, user.hashed_password)
    
    @staticmethod
    def change_password(
        db: Session,
        *,
        user_id: int,
        old_password: str,
        new_password: str
    ) -> bool:
        """
        Altera a senha de um usuário.
        
        
        Args:
            db: Sessão do banco
            user_id: ID do usuário
            old_password: Senha atual em texto plano
            new_password: Nova senha em texto plano
        
        Returns:
            True se alteração foi bem-sucedida, False caso contrário
        
        Raises:
            ValueError: Se nova senha é igual à antiga
        """
        if old_password == new_password:
            raise ValueError("Nova senha não pode ser igual à anterior")

        if not AuthService.verify_user_credentials(db, user_id=user_id, password=old_password):
            return False

        user = crud_user.get(db, id=user_id)
        if not user:
            return False
        

        user.hashed_password = get_password_hash(new_password)
        db.add(user)
        db.commit()
        return True


auth_service = AuthService()
