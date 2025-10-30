from sqlalchemy.orm import Session

from app.core.config import settings
from app.crud.user import user as crud_user
from app.schemas.user.request import UserCreate
from app.db.session import SessionLocal


def init_db(db: Session) -> None:
    """
    Inicializa o banco de dados com dados padrão.
    
    Cria um superusuário admin se não existir nenhum usuário no sistema.
    
    Args:
        db: Sessão do banco de dados
    """

    user = crud_user.get_by_email(db, email="admin@example.com")
    
    if not user:
        print("🔧 Criando usuário administrador padrão...")
        user_in = UserCreate(
            email="admin@example.com",
            password="admin123!@#",
            full_name="Administrador do Sistema",
        )
        user = crud_user.create(db, obj_in=user_in)
        

        user.is_superuser = True
        db.add(user)
        db.commit()
        db.refresh(user)
        
        print(f" Usuário admin criado: {user.email}")
        print(f"  IMPORTANTE: Altere a senha padrão após o primeiro login!")
    else:
        print("Usuário admin já existe.")


if __name__ == "__main__":
    print(" Inicializando banco de dados...")
    db = SessionLocal()
    try:
        init_db(db)
        print(" Banco de dados inicializado com sucesso!")
    finally:
        db.close()
