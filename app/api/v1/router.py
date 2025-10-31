from fastapi import APIRouter

from app.api.v1.endpoints import auth, reports, users, transactions


api_router = APIRouter()


api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"],
)


api_router.include_router(
    users.router,
    prefix="/users",
    tags=["Users"],
)

api_router.include_router(
    transactions.router,
    prefix="/transactions",
    tags=["Transactions"],
)

api_router.include_router(
    reports.router,
    prefix="/reports",
    tags=["Reports"],
)