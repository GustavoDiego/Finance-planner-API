from typing import Dict, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.transaction import Transaction, TransactionType, TransactionCategory
from app.crud.transaction import transaction as crud_transaction


class FinanceService:
    """
    Serviço com lógica de negócio complexa para finanças.
    """
    
    @staticmethod
    def get_monthly_summary(
        db: Session,
        *,
        user_id: int,
        year: int,
        month: int
    ) -> Dict:
        """
        Retorna resumo financeiro de um mês específico.
        
        Args:
            db: Sessão do banco
            user_id: ID do usuário
            year: Ano (ex: 2025)
            month: Mês (1-12)
        
        Returns:
            Dicionário com totais e breakdowns
        """
        # Cria range do mês
        date_from = datetime(year, month, 1)
        if month == 12:
            date_to = datetime(year + 1, 1, 1) - timedelta(seconds=1)
        else:
            date_to = datetime(year, month + 1, 1) - timedelta(seconds=1)
        
        return crud_transaction.get_summary(
            db,
            user_id=user_id,
            date_from=date_from,
            date_to=date_to
        )
    
    @staticmethod
    def get_yearly_summary(
        db: Session,
        *,
        user_id: int,
        year: int
    ) -> Dict:
        """
        Retorna resumo financeiro de um ano inteiro.
        
        Args:
            db: Sessão do banco
            user_id: ID do usuário
            year: Ano (ex: 2025)
        
        Returns:
            Dicionário com totais do ano
        """
        date_from = datetime(year, 1, 1)
        date_to = datetime(year, 12, 31, 23, 59, 59)
        
        return crud_transaction.get_summary(
            db,
            user_id=user_id,
            date_from=date_from,
            date_to=date_to
        )
    
    @staticmethod
    def get_monthly_breakdown(
        db: Session,
        *,
        user_id: int,
        year: int
    ) -> Dict[str, Dict]:
        """
        Retorna breakdown mensal de um ano inteiro.
        
        Args:
            db: Sessão do banco
            user_id: ID do usuário
            year: Ano
        
        Returns:
            Dicionário com dados de cada mês
        """
        breakdown = {}
        
        for month in range(1, 13):
            month_name = datetime(year, month, 1).strftime("%B")
            breakdown[month_name] = FinanceService.get_monthly_summary(
                db, user_id=user_id, year=year, month=month
            )
        
        return breakdown
    
    @staticmethod
    def get_highest_expenses(
        db: Session,
        *,
        user_id: int,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        limit: int = 10
    ) -> List[Dict]:
        """
        Retorna as maiores despesas do período.
        
        Args:
            db: Sessão do banco
            user_id: ID do usuário
            date_from: Data inicial (opcional)
            date_to: Data final (opcional)
            limit: Quantidade de resultados
        
        Returns:
            Lista com as maiores despesas
        """
        query = db.query(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.type == TransactionType.EXPENSE
        )
        
        if date_from:
            query = query.filter(Transaction.date >= date_from)
        if date_to:
            query = query.filter(Transaction.date <= date_to)
        
        transactions = query.order_by(Transaction.amount.desc()).limit(limit).all()
        
        return [
            {
                "id": t.id,
                "category": t.category.value,
                "amount": t.amount,
                "description": t.description,
                "date": t.date
            }
            for t in transactions
        ]
    
    @staticmethod
    def get_average_by_category(
        db: Session,
        *,
        user_id: int,
        transaction_type: TransactionType,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> Dict[str, float]:
        """
        Calcula média de transações por categoria.
        
        Args:
            db: Sessão do banco
            user_id: ID do usuário
            transaction_type: Tipo (income ou expense)
            date_from: Data inicial (opcional)
            date_to: Data final (opcional)
        
        Returns:
            Dicionário com média por categoria
        """
        query = db.query(
            Transaction.category,
            func.avg(Transaction.amount).label("average")
        ).filter(
            Transaction.user_id == user_id,
            Transaction.type == transaction_type
        )
        
        if date_from:
            query = query.filter(Transaction.date >= date_from)
        if date_to:
            query = query.filter(Transaction.date <= date_to)
        
        query = query.group_by(Transaction.category)
        
        return {
            row[0].value: row[1]
            for row in query.all()
        }
    
    @staticmethod
    def get_spending_trend(
        db: Session,
        *,
        user_id: int,
        days: int = 30
    ) -> List[Dict]:
        """
        Retorna tendência de gastos dos últimos N dias.
        
        Args:
            db: Sessão do banco
            user_id: ID do usuário
            days: Número de dias
        
        Returns:
            Lista com totais por dia
        """
        date_from = datetime.now() - timedelta(days=days)
        
        query = db.query(
            func.date(Transaction.date).label("date"),
            func.sum(Transaction.amount).label("total")
        ).filter(
            Transaction.user_id == user_id,
            Transaction.type == TransactionType.EXPENSE,
            Transaction.date >= date_from
        ).group_by(func.date(Transaction.date)).order_by(
            func.date(Transaction.date)
        )
        
        return [
            {
                "date": str(row[0]),
                "total": row[1] or 0
            }
            for row in query.all()
        ]
    
    @staticmethod
    def get_recurring_transactions(
        db: Session,
        *,
        user_id: int
    ) -> List[Dict]:
        """
        Retorna transações recorrentes do usuário.
        
        Args:
            db: Sessão do banco
            user_id: ID do usuário
        
        Returns:
            Lista de transações recorrentes com estimativa mensal
        """
        transactions = db.query(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.is_recurring == True
        ).all()
        
        total_monthly = sum(t.amount for t in transactions if t.type == TransactionType.EXPENSE)
        total_monthly_income = sum(t.amount for t in transactions if t.type == TransactionType.INCOME)
        
        return {
            "recurring_transactions": [
                {
                    "id": t.id,
                    "type": t.type.value,
                    "category": t.category.value,
                    "amount": t.amount,
                    "description": t.description
                }
                for t in transactions
            ],
            "monthly_expense_estimate": total_monthly,
            "monthly_income_estimate": total_monthly_income,
            "monthly_balance_estimate": total_monthly_income - total_monthly
        }
    
    @staticmethod
    def is_user_in_deficit(
        db: Session,
        *,
        user_id: int,
        days: int = 30
    ) -> bool:
        """
        Verifica se o usuário está em déficit (gastos > receitas).
        
        Args:
            db: Sessão do banco
            user_id: ID do usuário
            days: Período em dias
        
        Returns:
            True se em déficit, False caso contrário
        """
        date_from = datetime.now() - timedelta(days=days)
        
        income = db.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id == user_id,
            Transaction.type == TransactionType.INCOME,
            Transaction.date >= date_from
        ).scalar() or 0
        
        expense = db.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id == user_id,
            Transaction.type == TransactionType.EXPENSE,
            Transaction.date >= date_from
        ).scalar() or 0
        
        return expense > income


finance_service = FinanceService()
