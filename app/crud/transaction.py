from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from app.crud.base import CRUDBase
from app.models.transaction import Transaction, TransactionType, TransactionCategory
from app.schemas.transaction.request import TransactionCreate, TransactionUpdate, TransactionFilter


class CRUDTransaction(CRUDBase[Transaction, TransactionCreate, TransactionUpdate]):
    """
    CRUD específico para transações com métodos adicionais.
    """
    
    def create_with_user(
        self, db: Session, *, obj_in: TransactionCreate, user_id: int
    ) -> Transaction:
        """
        Cria uma transação associada a um usuário.
        
        Args:
            db: Sessão do banco
            obj_in: Dados da transação
            user_id: ID do usuário
        
        Returns:
            Transaction criada
        """
        obj_in_data = obj_in.model_dump()
        db_obj = Transaction(**obj_in_data, user_id=user_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_user(
        self, 
        db: Session, 
        *, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Transaction]:
        """
        Lista todas as transações de um usuário.
        
        Args:
            db: Sessão do banco
            user_id: ID do usuário
            skip: Offset de paginação
            limit: Limite de resultados
        
        Returns:
            Lista de transações do usuário
        """
        return (
            db.query(Transaction)
            .filter(Transaction.user_id == user_id)
            .order_by(Transaction.date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_id_and_user(
        self, db: Session, *, id: int, user_id: int
    ) -> Optional[Transaction]:
        """
        Busca uma transação por ID e usuário (garante ownership).
        
        Args:
            db: Sessão do banco
            id: ID da transação
            user_id: ID do usuário
        
        Returns:
            Transaction ou None
        """
        return (
            db.query(Transaction)
            .filter(Transaction.id == id, Transaction.user_id == user_id)
            .first()
        )

    def get_filtered(
        self,
        db: Session,
        *,
        user_id: int,
        filters: TransactionFilter,
        skip: int = 0,
        limit: int = 100
    ) -> List[Transaction]:
        """
        Busca transações com filtros avançados.
        
        Args:
            db: Sessão do banco
            user_id: ID do usuário
            filters: Objeto com filtros
            skip: Offset
            limit: Limite
        
        Returns:
            Lista de transações filtradas
        """
        query = db.query(Transaction).filter(Transaction.user_id == user_id)


        if filters.type:
            query = query.filter(Transaction.type == filters.type)

        if filters.category:
            query = query.filter(Transaction.category == filters.category)

        if filters.date_from:
            query = query.filter(Transaction.date >= filters.date_from)
        if filters.date_to:
            query = query.filter(Transaction.date <= filters.date_to)

        if filters.min_amount is not None:
            query = query.filter(Transaction.amount >= filters.min_amount)
        if filters.max_amount is not None:
            query = query.filter(Transaction.amount <= filters.max_amount)

        if filters.is_recurring is not None:
            query = query.filter(Transaction.is_recurring == filters.is_recurring)

        return query.order_by(Transaction.date.desc()).offset(skip).limit(limit).all()

    def get_summary(
        self,
        db: Session,
        *,
        user_id: int,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Calcula resumo financeiro do usuário.
        
        Args:
            db: Sessão do banco
            user_id: ID do usuário
            date_from: Data inicial (opcional)
            date_to: Data final (opcional)
        
        Returns:
            Dicionário com totais, saldo e breakdown por categoria
        """
        query = db.query(Transaction).filter(Transaction.user_id == user_id)

        if date_from:
            query = query.filter(Transaction.date >= date_from)
        if date_to:
            query = query.filter(Transaction.date <= date_to)

        transactions = query.all()

        total_income = sum(t.amount for t in transactions if t.type == TransactionType.INCOME)
        total_expense = sum(t.amount for t in transactions if t.type == TransactionType.EXPENSE)
        balance = total_income - total_expense

        income_by_category: Dict[str, float] = {}
        expense_by_category: Dict[str, float] = {}

        for transaction in transactions:
            category_name = transaction.category.value
            
            if transaction.type == TransactionType.INCOME:
                income_by_category[category_name] = income_by_category.get(category_name, 0) + transaction.amount
            else:
                expense_by_category[category_name] = expense_by_category.get(category_name, 0) + transaction.amount

        return {
            "total_income": total_income,
            "total_expense": total_expense,
            "balance": balance,
            "transaction_count": len(transactions),
            "income_by_category": income_by_category,
            "expense_by_category": expense_by_category,
        }

    def get_totals(
        self,
        db: Session,
        *,
        user_id: int,
        transactions: List[Transaction]
    ) -> Dict[str, float]:
        """
        Calcula totais de uma lista de transações.
        
        Args:
            db: Sessão do banco
            user_id: ID do usuário
            transactions: Lista de transações
        
        Returns:
            Dicionário com total_income, total_expense e balance
        """
        total_income = sum(t.amount for t in transactions if t.type == TransactionType.INCOME)
        total_expense = sum(t.amount for t in transactions if t.type == TransactionType.EXPENSE)
        balance = total_income - total_expense

        return {
            "total_income": total_income,
            "total_expense": total_expense,
            "balance": balance,
        }

    def delete_by_user(
        self, db: Session, *, id: int, user_id: int
    ) -> Optional[Transaction]:
        """
        Deleta uma transação (garante ownership).
        
        Args:
            db: Sessão do banco
            id: ID da transação
            user_id: ID do usuário
        
        Returns:
            Transaction deletada ou None
        """
        obj = self.get_by_id_and_user(db, id=id, user_id=user_id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj


transaction = CRUDTransaction(Transaction)
