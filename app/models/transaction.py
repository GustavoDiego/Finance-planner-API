from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.db.base_class import Base


class TransactionType(str, enum.Enum):
    """Tipo da transação financeira."""
    INCOME = "income"   
    EXPENSE = "expense"    


class TransactionCategory(str, enum.Enum):
    """Categorias de transações."""
 
    SALARY = "salary"             
    FREELANCE = "freelance"       
    INVESTMENT = "investment"     
    BUSINESS = "business"         
    OTHER_INCOME = "other_income"  


    FOOD = "food"                
    TRANSPORT = "transport"        
    HOUSING = "housing"            
    UTILITIES = "utilities"        
    HEALTHCARE = "healthcare"      
    EDUCATION = "education"        
    ENTERTAINMENT = "entertainment" 
    SHOPPING = "shopping"          
    SUBSCRIPTION = "subscription"  
    OTHER_EXPENSE = "other_expense"


class Transaction(Base):
    """
    Model de transação financeira.
    
    Representa receitas (income) e despesas (expense) do usuário.
    
    Attributes:
        id: Identificador único da transação
        user_id: ID do usuário (FK para users)
        type: Tipo (income ou expense)
        category: Categoria da transação
        amount: Valor da transação
        description: Descrição/observação
        date: Data da transação
        is_recurring: Se é transação recorrente
        created_at: Data de criação do registro
        updated_at: Data da última atualização
        user: Relacionamento com User
    """
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    type = Column(SQLEnum(TransactionType), nullable=False, index=True)
    category = Column(SQLEnum(TransactionCategory), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    description = Column(String, nullable=True)
    date = Column(DateTime(timezone=True), nullable=False, index=True)
    is_recurring = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


    user = relationship("User", back_populates="transactions")
