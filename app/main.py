from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from contextlib import asynccontextmanager

from app.api.v1.router import api_router
from app.core.config import settings
from app.db.session import engine
from app.db.base import Base


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="API para gerenciamento financeiro pessoal, incluindo autenticação, usuários, transações e relatórios.",
    openapi_tags=[
        {
            "name": "Authentication",
            "description": "Operações de autenticação e autorização (registro, login, refresh token)",
        },
        {
            "name": "Users",
            "description": "Gerenciamento de usuários (CRUD, perfis, permissões)",
        },
        {
            "name": "Transactions",
            "description": "Gerenciamento de transações financeiras (despesas e receitas)",
        },
        {
            "name": "Reports",
            "description": "Relatórios e análises estatísticas financeiras",
        },
    ],
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    contact={
        "name": "Gustavo Diego",
        "email": "gustavodiego298@gmail.com",
        "url": "https://github.com/GustavoDiego/finance-planner-api",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get(
    "/",
    include_in_schema=False,
    summary="Raiz da API",
    description="Redireciona para a documentação Swagger"
)
async def root():

    return RedirectResponse(url="/docs")


@app.get(
    "/health",
    tags=["Health Check"],
    summary="Verificação de saúde da API",
    description="Endpoint para verificar se a API está online e funcionando"
)
async def health_check():

    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
    }

@asynccontextmanager
async def lifespan(app: FastAPI):
    
    print(f"🚀 {settings.PROJECT_NAME} v{settings.VERSION} iniciada!")
    print(f"📚 Documentação disponível em: http://localhost:8000/docs")
    print(f"💾 Usando SQLite: {settings.DATABASE_URL}")
    
    yield
    
    
    print(f"👋 {settings.PROJECT_NAME} encerrada!")
async def shutdown_event():

    print(f"👋 {settings.PROJECT_NAME} encerrada!")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

