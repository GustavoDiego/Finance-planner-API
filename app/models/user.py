from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func

from app.db.base_class import Base


class User(Base):
    """
    Model de usuário do sistema.
    
    Representa a tabela 'users' no banco de dados.
    
    Attributes:
        id: Identificador único do usuário
        email: Email único do usuário (usado para login)
        hashed_password: Senha hasheada com bcrypt
        full_name: Nome completo do usuário (opcional)
        is_active: Status do usuário (ativo/inativo)
        is_superuser: Indica se é administrador
        created_at: Data/hora de criação do registro
        updated_at: Data/hora da última atualização
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
