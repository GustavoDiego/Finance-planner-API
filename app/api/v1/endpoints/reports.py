from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from datetime import datetime, timedelta
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
    response_description="Relatório do mês retornado com sucesso",
    responses={
        200: {
            "description": "Relatório mensal gerado com sucesso",
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "message": "Monthly report retrieved successfully",
                        "data": {
                            "summary": {
                                "total_income": 5000.00,
                                "total_expense": 2500.00,
                                "balance": 2500.00,
                                "transaction_count": 15,
                                "income_by_category": {"salary": 5000.00},
                                "expense_by_category": {"food": 800.00, "transport": 300.00}
                            }
                        }
                    }
                }
            }
        },
        400: {
            "description": "Parâmetros inválidos",
            "content": {
                "application/json": {
                    "example": {"detail": "Mês deve estar entre 1 e 12"}
                }
            }
        }
    }
)
def get_monthly_report(
    year: int = Query(..., ge=2000, le=2100, description="Ano (ex: 2025)"),
    month: int = Query(..., ge=1, le=12, description="Mês (1-12)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Retorna relatório financeiro de um mês específico.
    
    ## Autenticação Obrigatória
    - Requer token JWT válido
    
    ## Parâmetros
    - **year**: Ano (ex: 2025)
    - **month**: Mês (1-12)
    
    ## Retorna
    - Total de receitas do mês
    - Total de despesas do mês
    - Saldo do mês
    - Breakdown por categoria
    - Quantidade de transações
    
    ## Exemplo
    - `/api/v1/reports/monthly/2025/10` - Outubro de 2025
    
    ## Erros
    - **400**: Parâmetros fora do intervalo válido
    """
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
    response_description="Relatório do ano retornado com sucesso",
    responses={
        200: {
            "description": "Relatório anual gerado com sucesso",
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "message": "Yearly report retrieved successfully",
                        "data": {
                            "summary": {
                                "total_income": 60000.00,
                                "total_expense": 30000.00,
                                "balance": 30000.00,
                                "transaction_count": 180,
                                "income_by_category": {"salary": 60000.00},
                                "expense_by_category": {
                                    "food": 9600.00,
                                    "transport": 3600.00,
                                    "housing": 15000.00
                                }
                            }
                        }
                    }
                }
            }
        }
    }
)
def get_yearly_report(
    year: int = Query(..., ge=2000, le=2100, description="Ano (ex: 2025)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Retorna relatório financeiro de um ano inteiro.
    
    ## Autenticação Obrigatória
    - Requer token JWT válido
    
    ## Parâmetros
    - **year**: Ano (ex: 2025)
    
    ## Retorna
    - Total anual de receitas
    - Total anual de despesas
    - Saldo anual
    - Breakdown por categoria
    - Quantidade total de transações do ano
    
    ## Exemplo
    - `/api/v1/reports/yearly/2025` - Ano de 2025
    """
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
    response_description="Breakdown retornado com sucesso",
    responses={
        200: {
            "description": "Breakdown mensal do ano",
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "message": "Yearly breakdown retrieved successfully",
                        "data": {
                            "breakdown": {
                                "January": {
                                    "total_income": 5000,
                                    "total_expense": 2500,
                                    "balance": 2500,
                                    "transaction_count": 15,
                                    "income_by_category": {},
                                    "expense_by_category": {}
                                },
                                "February": {
                                    "total_income": 5000,
                                    "total_expense": 2600,
                                    "balance": 2400,
                                    "transaction_count": 16,
                                    "income_by_category": {},
                                    "expense_by_category": {}
                                }
                            }
                        }
                    }
                }
            }
        }
    }
)
def get_yearly_breakdown(
    year: int = Query(..., ge=2000, le=2100, description="Ano (ex: 2025)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Retorna breakdown mensal de um ano inteiro.
    
    ## Autenticação Obrigatória
    - Requer token JWT válido
    
    ## Parâmetros
    - **year**: Ano (ex: 2025)
    
    ## Retorna
    - Dados de cada mês do ano
    - Totais, balanço e categorias por mês
    - 12 meses completos
    
    ## Uso
    Ideal para visualizar evolução mensal em um gráfico de linha.
    """
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
    response_description="Maiores despesas retornadas",
    responses={
        200: {
            "description": "Top 10 maiores despesas",
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "message": "Highest expenses retrieved successfully",
                        "data": {
                            "expenses": [
                                {
                                    "id": 1,
                                    "category": "housing",
                                    "amount": 1500.00,
                                    "description": "Aluguel",
                                    "date": "2025-10-30T00:00:00"
                                }
                            ],
                            "period_days": 30
                        }
                    }
                }
            }
        }
    }
)
def get_highest_expenses(
    days: int = Query(30, ge=1, le=365, description="Últimos N dias"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Retorna as 10 maiores despesas do período.
    
    ## Autenticação Obrigatória
    - Requer token JWT válido
    
    ## Parâmetros
    - **days**: Período em dias (padrão: 30, máximo: 365)
    
    ## Retorna
    - Lista das 10 maiores despesas
    - Ordenadas por valor (maior para menor)
    - Categoria, descrição e data de cada despesa
    
    ## Exemplos
    - `/api/v1/reports/highest-expenses?days=30` - Últimos 30 dias
    - `/api/v1/reports/highest-expenses?days=365` - Último ano
    
    ## Uso
    Ideal para identificar principais centros de gastos.
    """
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
    response_description="Tendência de gastos retornada",
    responses={
        200: {
            "description": "Tendência de gastos por dia",
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "message": "Spending trend retrieved successfully",
                        "data": {
                            "trend": [
                                {"date": "2025-10-01", "total": 150.00},
                                {"date": "2025-10-02", "total": 200.00}
                            ],
                            "period_days": 30
                        }
                    }
                }
            }
        }
    }
)
def get_spending_trend(
    days: int = Query(30, ge=1, le=365, description="Últimos N dias"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Retorna tendência de gastos dos últimos N dias.
    
    Útil para visualizar padrões de gastos em gráficos.
    
    ## Autenticação Obrigatória
    - Requer token JWT válido
    
    ## Parâmetros
    - **days**: Período em dias (padrão: 30, máximo: 365)
    
    ## Retorna
    - Lista com totais de gastos por dia
    - Ordenado cronologicamente
    - Datas sem transações aparecem como zero
    
    ## Exemplos
    - `/api/v1/reports/spending-trend?days=30` - Últimos 30 dias
    - `/api/v1/reports/spending-trend?days=7` - Última semana
    
    ## Uso
    Perfeito para gráficos de linha mostrando evolução de gastos.
    """
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
    response_description="Transações recorrentes retornadas",
    responses={
        200: {
            "description": "Transações recorrentes do usuário",
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "message": "Recurring transactions retrieved successfully",
                        "data": {
                            "recurring": {
                                "recurring_transactions": [
                                    {
                                        "id": 1,
                                        "type": "income",
                                        "category": "salary",
                                        "amount": 5000.00,
                                        "description": "Salário mensal"
                                    }
                                ],
                                "monthly_expense_estimate": 2500.00,
                                "monthly_income_estimate": 5000.00,
                                "monthly_balance_estimate": 2500.00
                            }
                        }
                    }
                }
            }
        }
    }
)
def get_recurring_transactions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Retorna todas as transações recorrentes do usuário.
    
    Inclui estimativa mensal de receitas e despesas.
    
    ## Autenticação Obrigatória
    - Requer token JWT válido
    
    ## Retorna
    - Lista de transações recorrentes (is_recurring=true)
    - Estimativa mensal de despesas recorrentes
    - Estimativa mensal de receitas recorrentes
    - Saldo mensal estimado com recorrentes
    
    ## Uso
    - Planejamento de orçamento mensal
    - Identificar receitas/despesas fixas
    - Calcular mínimo necessário para cobrir custos
    
    ## Exemplo
    Se tem:
    - Salário: R$ 5.000/mês (recorrente)
    - Aluguel: R$ 1.500/mês (recorrente)
    - Internet: R$ 100/mês (recorrente)
    
    Estimativa mensal será:
    - Receitas: R$ 5.000
    - Despesas: R$ 1.600
    - Saldo: R$ 3.400
    """
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
    response_description="Status financeiro do usuário",
    responses={
        200: {
            "description": "Status financeiro retornado",
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "message": "Excelente: Suas receitas excedem suas despesas. Continue assim!",
                        "data": {
                            "financial_status": "superávit",
                            "is_in_deficit": False,
                            "period_days": 30
                        }
                    }
                }
            }
        }
    }
)
def get_financial_health(
    days: int = Query(30, ge=1, le=365, description="Últimos N dias"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Retorna verificação de saúde financeira do usuário.
    
    Indica se o usuário está em déficit ou superávit.
    
    ## Autenticação Obrigatória
    - Requer token JWT válido
    
    ## Parâmetros
    - **days**: Período em dias (padrão: 30, máximo: 365)
    
    ## Retorna
    - Status: "déficit" ou "superávit"
    - Booleano indicando déficit
    - Período analisado
    - Mensagem de recomendação
    
    ## Dois Cenários
    
    ### Déficit (Despesas > Receitas):
    ```
    {
        "financial_status": "déficit",
        "is_in_deficit": true,
        "message": "Atenção: Suas despesas excedem suas receitas..."
    }
    ```
    
    ### Superávit (Receitas > Despesas):
    ```
    {
        "financial_status": "superávit",
        "is_in_deficit": false,
        "message": "Excelente: Suas receitas excedem suas despesas..."
    }
    ```
    
    ## Uso
    - Verificar saúde financeira da conta
    - Alertar usuário sobre déficit
    - Dashboard indicador gráfico
    """
    is_deficit = finance_service.is_user_in_deficit(
        db, 
        user_id=current_user.id, 
        days=days
    )
    
    status_text = "déficit" if is_deficit else "superávit"
    message = (
        "Atenção: Suas despesas excedem suas receitas. Considere revisar seu orçamento."
        if is_deficit
        else "Excelente: Suas receitas excedem suas despesas. Continue assim!"
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
