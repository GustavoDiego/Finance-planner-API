from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime

from app.api.deps import get_db, get_current_active_user
from app.crud.transaction import transaction as crud_transaction
from app.models.user import User
from app.schemas.transaction.request import TransactionCreate, TransactionUpdate, TransactionFilter
from app.schemas.transaction.response import TransactionResponse, TransactionListResponse, TransactionSummary
from app.schemas.response import ResponseEnvelope

router = APIRouter()


@router.post(
    "/",
    response_model=ResponseEnvelope,
    status_code=status.HTTP_201_CREATED,
    summary="Criar nova transação",
    response_description="Transação criada com sucesso"
)
def create_transaction(
    *,
    db: Session = Depends(get_db),
    transaction_in: TransactionCreate,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Cria uma nova transação financeira (receita ou despesa).
    
    ## Autenticação Obrigatória
    - Requer token JWT válido
    - Transação será associada ao usuário logado
    
    ## Parâmetros
    - **type**: Tipo da transação (income ou expense)
    - **category**: Categoria (salary, food, transport, etc)
    - **amount**: Valor (deve ser positivo)
    - **description**: Descrição opcional
    - **date**: Data da transação
    - **is_recurring**: Se é transação recorrente
    
    ## Tipos e Categorias
    
    ### Income (Receitas):
    - salary, freelance, investment, business, other_income
    
    ### Expense (Despesas):
    - food, transport, housing, utilities, healthcare, education,
      entertainment, shopping, subscription, other_expense
    
    ## Retorna
    - Dados da transação criada
    - Status HTTP 201 Created
    """
    transaction = crud_transaction.create_with_user(
        db=db, obj_in=transaction_in, user_id=current_user.id
    )
    
    return ResponseEnvelope(
        status="success",
        message="Transaction created successfully",
        data={"transaction": TransactionResponse.model_validate(transaction)}
    )


@router.get(
    "/",
    response_model=ResponseEnvelope,
    status_code=status.HTTP_200_OK,
    summary="Listar transações do usuário",
    response_description="Lista de transações retornada com sucesso"
)
def list_transactions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    skip: int = Query(0, ge=0, description="Offset de paginação"),
    limit: int = Query(100, ge=1, le=1000, description="Limite de resultados")
) -> Any:
    """
    Lista todas as transações do usuário logado com paginação.
    
    ## Autenticação Obrigatória
    - Requer token JWT válido
    - Retorna apenas transações do usuário logado
    
    ## Parâmetros de Query
    - **skip**: Offset de paginação (padrão: 0)
    - **limit**: Limite de resultados (padrão: 100, máx: 1000)
    
    ## Retorna
    - Lista de transações ordenadas por data (mais recente primeiro)
    - Total de transações
    - Total de receitas (income)
    - Total de despesas (expense)
    - Saldo (balance = receitas - despesas)
    
    ## Exemplo
    - `/transactions?skip=0&limit=20` - Primeiras 20 transações
    - `/transactions?skip=20&limit=20` - Próximas 20 transações
    """
    transactions = crud_transaction.get_by_user(
        db=db, user_id=current_user.id, skip=skip, limit=limit
    )

    totals = crud_transaction.get_totals(
        db=db, user_id=current_user.id, transactions=transactions
    )
    
    return ResponseEnvelope(
        status="success",
        message="Transactions retrieved successfully",
        data={
            "transactions": [TransactionResponse.model_validate(t) for t in transactions],
            "total": len(transactions),
            "total_income": totals["total_income"],
            "total_expense": totals["total_expense"],
            "balance": totals["balance"]
        }
    )


@router.post(
    "/filter",
    response_model=ResponseEnvelope,
    status_code=status.HTTP_200_OK,
    summary="Filtrar transações",
    response_description="Transações filtradas retornadas com sucesso"
)
def filter_transactions(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    filters: TransactionFilter,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
) -> Any:
    """
    Filtra transações com múltiplos critérios.
    
    ## Autenticação Obrigatória
    - Requer token JWT válido
    
    ## Filtros Disponíveis
    - **type**: Filtrar por tipo (income ou expense)
    - **category**: Filtrar por categoria
    - **date_from**: Data inicial (ISO 8601)
    - **date_to**: Data final (ISO 8601)
    - **min_amount**: Valor mínimo
    - **max_amount**: Valor máximo
    - **is_recurring**: Apenas transações recorrentes (true/false)
    
    ## Exemplos de Uso
    
    ### Despesas de alimentação em outubro:
    ```
    {
        "type": "expense",
        "category": "food",
        "date_from": "2025-10-01T00:00:00",
        "date_to": "2025-10-31T23:59:59"
    }
    ```
    
    ### Transações acima de R$ 100:
    ```
    {
        "min_amount": 100.00
    }
    ```
    
    ## Retorna
    - Lista de transações filtradas
    - Totais calculados com base nos filtros
    """
    transactions = crud_transaction.get_filtered(
        db=db,
        user_id=current_user.id,
        filters=filters,
        skip=skip,
        limit=limit
    )
    
    totals = crud_transaction.get_totals(
        db=db, user_id=current_user.id, transactions=transactions
    )
    
    return ResponseEnvelope(
        status="success",
        message="Filtered transactions retrieved successfully",
        data={
            "transactions": [TransactionResponse.model_validate(t) for t in transactions],
            "total": len(transactions),
            "total_income": totals["total_income"],
            "total_expense": totals["total_expense"],
            "balance": totals["balance"]
        }
    )


@router.get(
    "/summary",
    response_model=ResponseEnvelope,
    status_code=status.HTTP_200_OK,
    summary="Obter resumo financeiro",
    response_description="Resumo financeiro retornado com sucesso"
)
def get_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    date_from: datetime = Query(None, description="Data inicial do período"),
    date_to: datetime = Query(None, description="Data final do período")
) -> Any:
    """
    Retorna resumo financeiro detalhado do usuário.
    
    ## Autenticação Obrigatória
    - Requer token JWT válido
    
    ## Parâmetros de Query
    - **date_from**: Data inicial (opcional, ISO 8601)
    - **date_to**: Data final (opcional, ISO 8601)
    - Se não fornecidas, considera todas as transações
    
    ## Retorna
    - **total_income**: Total de receitas
    - **total_expense**: Total de despesas
    - **balance**: Saldo (receitas - despesas)
    - **transaction_count**: Quantidade de transações
    - **income_by_category**: Receitas agrupadas por categoria
    - **expense_by_category**: Despesas agrupadas por categoria
    
    ## Exemplos
    - `/summary` - Resumo de todas as transações
    - `/summary?date_from=2025-10-01T00:00:00&date_to=2025-10-31T23:59:59` - Outubro/2025
    
    ## Uso
    Ideal para dashboards, relatórios e análise de gastos por categoria.
    """
    summary = crud_transaction.get_summary(
        db=db,
        user_id=current_user.id,
        date_from=date_from,
        date_to=date_to
    )
    
    summary_data = TransactionSummary(
        period_start=date_from or datetime.min,
        period_end=date_to or datetime.now(),
        total_income=summary["total_income"],
        total_expense=summary["total_expense"],
        balance=summary["balance"],
        transaction_count=summary["transaction_count"],
        income_by_category=summary["income_by_category"],
        expense_by_category=summary["expense_by_category"]
    )
    
    return ResponseEnvelope(
        status="success",
        message="Summary retrieved successfully",
        data={"summary": summary_data}
    )


@router.get(
    "/{transaction_id}",
    response_model=ResponseEnvelope,
    status_code=status.HTTP_200_OK,
    summary="Buscar transação por ID",
    response_description="Transação encontrada"
)
def get_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Busca uma transação específica por ID.
    
    ## Autenticação Obrigatória
    - Requer token JWT válido
    - Usuário só pode visualizar suas próprias transações
    
    ## Parâmetros
    - **transaction_id**: ID da transação
    
    ## Retorna
    - Dados completos da transação
    
    ## Erros
    - **404**: Transação não encontrada ou não pertence ao usuário
    """
    transaction = crud_transaction.get_by_id_and_user(
        db=db, id=transaction_id, user_id=current_user.id
    )
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    
    return ResponseEnvelope(
        status="success",
        message="Transaction found",
        data={"transaction": TransactionResponse.model_validate(transaction)}
    )


@router.put(
    "/{transaction_id}",
    response_model=ResponseEnvelope,
    status_code=status.HTTP_200_OK,
    summary="Atualizar transação",
    response_description="Transação atualizada com sucesso"
)
def update_transaction(
    transaction_id: int,
    transaction_in: TransactionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Atualiza uma transação existente.
    
    ## Autenticação Obrigatória
    - Requer token JWT válido
    - Usuário só pode atualizar suas próprias transações
    
    ## Parâmetros
    - **transaction_id**: ID da transação
    - Todos os campos são opcionais (atualização parcial)
    
    ## Campos Atualizáveis
    - type, category, amount, description, date, is_recurring
    
    ## Retorna
    - Dados da transação atualizada
    
    ## Erros
    - **404**: Transação não encontrada
    """
    transaction = crud_transaction.get_by_id_and_user(
        db=db, id=transaction_id, user_id=current_user.id
    )
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    
    transaction = crud_transaction.update(
        db=db, db_obj=transaction, obj_in=transaction_in
    )
    
    return ResponseEnvelope(
        status="success",
        message="Transaction updated successfully",
        data={"transaction": TransactionResponse.model_validate(transaction)}
    )


@router.delete(
    "/{transaction_id}",
    response_model=ResponseEnvelope,
    status_code=status.HTTP_200_OK,
    summary="Deletar transação",
    response_description="Transação deletada com sucesso"
)
def delete_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Deleta uma transação.
    
    ## Autenticação Obrigatória
    - Requer token JWT válido
    - Usuário só pode deletar suas próprias transações
    
    ## Parâmetros
    - **transaction_id**: ID da transação
    
    ## Atenção
    - Esta operação é **irreversível**
    - A transação será permanentemente removida
    
    ## Retorna
    - Mensagem de sucesso
    
    ## Erros
    - **404**: Transação não encontrada
    """
    transaction = crud_transaction.delete_by_user(
        db=db, id=transaction_id, user_id=current_user.id
    )
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    
    return ResponseEnvelope(
        status="success",
        message="Transaction deleted successfully",
        data=None
    )
