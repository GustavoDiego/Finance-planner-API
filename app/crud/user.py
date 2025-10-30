from typing import Optional
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.user import User
from app.schemas.user.request import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password
from typing import Union, Dict, Any

class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    """CRUD específico para usuários com métodos adicionais."""
    
    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        """Busca usuário por email."""
        return db.query(User).filter(User.email == email).first()

    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        """Cria usuário com senha hasheada."""
        db_obj = User(
            email=obj_in.email,
            hashed_password=get_password_hash(obj_in.password),
            full_name=obj_in.full_name,
            is_active=True,
            is_superuser=False,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, *, db_obj: User, obj_in: Union[UserUpdate, Dict[str, Any]]
    ) -> User:
        """Atualiza usuário, hasheando senha se fornecida."""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        
        if "password" in update_data:
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password
        
        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def authenticate(self, db: Session, *, email: str, password: str) -> Optional[User]:
        """Autentica usuário com email e senha."""
        user = self.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def is_active(self, user: User) -> bool:
        """Verifica se usuário está ativo."""
        return user.is_active

    def is_superuser(self, user: User) -> bool:
        """Verifica se usuário é superusuário."""
        return user.is_superuser




user = CRUDUser(User)
