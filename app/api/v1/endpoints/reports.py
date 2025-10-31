from fastapi import APIRouter, Path, Query, Depends, HTTPException, status
from datetime import datetime, timedelta
from typing import Any
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_active_user
from app.models.user import User
from app.schemas.response import ResponseEnvelope
from app.services.finance_service import finance_service

router = APIRouter()


@router.get(
    "/monthly/{year}/{month}",
    response_model=ResponseEnvelope,
    status_code=status.HTTP_200_OK,
    summary="Relatório mensal",
    response_description="Relatório do mês retornado com sucesso"
)
def get_monthly_report(
    year: int = Path(..., ge=2000, le=2100, description="Ano (ex: 2025)"), 
    month: int = Path(..., ge=1, le=12, description="Mês (1-12)"),         
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Retorna relatório financeiro de um mês específico."""
    try:
        summary = finance_service.get_monthly_summary(
            db, 
            user_id=current_user.id, 
            year=year, 
            month=month
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    return ResponseEnvelope(
        status="success",
        message="Monthly report retrieved successfully",
        data={"summary": summary}
    )


@router.get(
    "/yearly/{year}",
    response_model=ResponseEnvelope,
    status_code=status.HTTP_200_OK,
    summary="Relatório anual",
    response_description="Relatório do ano retornado com sucesso"
)
def get_yearly_report(
    year: int = Path(..., ge=2000, le=2100, description="Ano (ex: 2025)"),  
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Retorna relatório financeiro de um ano inteiro."""
    try:
        summary = finance_service.get_yearly_summary(
            db, 
            user_id=current_user.id, 
            year=year
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    return ResponseEnvelope(
        status="success",
        message="Yearly report retrieved successfully",
        data={"summary": summary}
    )


@router.get(
    "/yearly-breakdown/{year}",
    response_model=ResponseEnvelope,
    status_code=status.HTTP_200_OK,
    summary="Breakdown mensal do ano",
    response_description="Breakdown retornado com sucesso"
)
def get_yearly_breakdown(
    year: int = Path(..., ge=2000, le=2100, description="Ano (ex: 2025)"), 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Retorna breakdown mensal de um ano inteiro."""
    try:
        breakdown = finance_service.get_monthly_breakdown(
            db, 
            user_id=current_user.id, 
            year=year
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    return ResponseEnvelope(
        status="success",
        message="Yearly breakdown retrieved successfully",
        data={"breakdown": breakdown}
    )


@router.get(
    "/highest-expenses",
    response_model=ResponseEnvelope,
    status_code=status.HTTP_200_OK,
    summary="Top 10 maiores despesas",
    response_description="Maiores despesas retornadas"
)
def get_highest_expenses(
    days: int = Query(30, ge=1, le=365, description="Últimos N dias"), 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Retorna as 10 maiores despesas do período."""
    date_from = datetime.now() - timedelta(days=days)
    expenses = finance_service.get_highest_expenses(
        db,
        user_id=current_user.id,
        date_from=date_from,
        limit=10
    )
    
    return ResponseEnvelope(
        status="success",
        message="Highest expenses retrieved successfully",
        data={"expenses": expenses, "period_days": days}
    )


@router.get(
    "/spending-trend",
    response_model=ResponseEnvelope,
    status_code=status.HTTP_200_OK,
    summary="Tendência de gastos",
    response_description="Tendência de gastos retornada"
)
def get_spending_trend(
    days: int = Query(30, ge=1, le=365, description="Últimos N dias"), 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Retorna tendência de gastos dos últimos N dias."""
    trend = finance_service.get_spending_trend(
        db, 
        user_id=current_user.id, 
        days=days
    )
    
    return ResponseEnvelope(
        status="success",
        message="Spending trend retrieved successfully",
        data={"trend": trend, "period_days": days}
    )


@router.get(
    "/recurring-transactions",
    response_model=ResponseEnvelope,
    status_code=status.HTTP_200_OK,
    summary="Transações recorrentes",
    response_description="Transações recorrentes retornadas"
)
def get_recurring_transactions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Retorna todas as transações recorrentes do usuário."""
    recurring = finance_service.get_recurring_transactions(
        db, 
        user_id=current_user.id
    )
    
    return ResponseEnvelope(
        status="success",
        message="Recurring transactions retrieved successfully",
        data={"recurring": recurring}
    )


@router.get(
    "/health-check",
    response_model=ResponseEnvelope,
    status_code=status.HTTP_200_OK,
    summary="Verificação de saúde financeira",
    response_description="Status financeiro do usuário"
)
def get_financial_health(
    days: int = Query(30, ge=1, le=365, description="Últimos N dias"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Retorna verificação de saúde financeira do usuário."""
    is_deficit = finance_service.is_user_in_deficit(
        db, 
        user_id=current_user.id, 
        days=days
    )
    
    status_text = "déficit" if is_deficit else "superávit"
    message = (
        " Atenção: Suas despesas excedem suas receitas. Considere revisar seu orçamento."
        if is_deficit
        else " Excelente: Suas receitas excedem suas despesas. Continue assim!"
    )
    
    return ResponseEnvelope(
        status="success",
        message=message,
        data={
            "financial_status": status_text,
            "is_in_deficit": is_deficit,
            "period_days": days
        }
    )
