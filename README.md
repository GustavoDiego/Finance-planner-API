# Finance Planner API

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.13+-3776AB?style=flat-square&logo=python)](https://www.python.org/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0+-FF0000?style=flat-square&logo=sqlalchemy)](https://www.sqlalchemy.org/)
[![JWT](https://img.shields.io/badge/JWT-Authentication-FF6B6B?style=flat-square)](https://jwt.io/)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Ativo-success?style=flat-square)](README.md)

API completa para **planejamento financeiro pessoal** com autenticação JWT, CRUD de transações e análises financeiras avançadas.

## 🎯 Features Principais



## 🚀 Quick Start

### Pré-requisitos

- Python 3.13+
- Poetry
- Git

### Instalação

1. **Clone o repositório**
```
git clone https://github.com/GustavoDiego/finance-planner-api.git
cd finance-planner-api
```

2. **Instale as dependências**
```
poetry install
```

3. **Configure as variáveis de ambiente**
```
cp .env.example .env
# Edite .env com suas configurações
```

4. **Crie o banco de dados e admin**
```
python -m app.db.init_db
```

5. **Rode a aplicação**
```
poetry run python run.py
# ou
uvicorn app.main:app --reload
```

6. **Acesse a documentação**
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 📖 Guia de Uso

### 1️⃣ Registrar Novo Usuário

```
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "joao@example.com",
    "password": "SenhaSegura123!",
    "full_name": "João Silva"
  }'
```

**Response:**
```
{
  "status": "success",
  "message": "User registered successfully",
  "data": {
    "user": {
      "id": 1,
      "email": "joao@example.com",
      "full_name": "João Silva",
      "is_active": true,
      "created_at": "2025-10-30T20:10:00"
    },
    "tokens": {
      "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
      "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
      "token_type": "bearer"
    }
  }
}
```

### 2️⃣ Fazer Login

```
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=joao@example.com&password=SenhaSegura123!"
```

### 3️⃣ Alterar Senha

```
curl -X POST "http://localhost:8000/api/v1/auth/change-password" \
  -H "Authorization: Bearer SEU_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "old_password": "SenhaSegura123!",
    "new_password": "NovaSenha456!"
  }'
```

### 4️⃣ Criar Transação (Despesa)

```
curl -X POST "http://localhost:8000/api/v1/transactions/" \
  -H "Authorization: Bearer SEU_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "expense",
    "category": "food",
    "amount": 150.50,
    "description": "Almoço no restaurante",
    "date": "2025-10-30T12:30:00",
    "is_recurring": false
  }'
```

### 5️⃣ Filtrar Transações

```
curl -X POST "http://localhost:8000/api/v1/transactions/filter" \
  -H "Authorization: Bearer SEU_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "expense",
    "category": "food",
    "date_from": "2025-10-01T00:00:00",
    "date_to": "2025-10-31T23:59:59",
    "min_amount": 50.00
  }'
```

### 6️⃣ Obter Relatório Mensal

```
curl -X GET "http://localhost:8000/api/v1/reports/monthly/2025/10" \
  -H "Authorization: Bearer SEU_ACCESS_TOKEN"
```

### 7️⃣ Verificar Saúde Financeira

```
curl -X GET "http://localhost:8000/api/v1/reports/health-check?days=30" \
  -H "Authorization: Bearer SEU_ACCESS_TOKEN"
```

### 8️⃣ Obter Dados do Usuário Logado

```
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer SEU_ACCESS_TOKEN"
```

### 9️⃣ Renovar Token

```
curl -X POST "http://localhost:8000/api/v1/auth/refresh" \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "SEU_REFRESH_TOKEN"
  }'
```

---

## 📋 Endpoints Disponíveis

### 🔓 Autenticação (Públicos)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `POST` | `/api/v1/auth/register` | Registrar novo usuário |
| `POST` | `/api/v1/auth/login` | Login (OAuth2) |

### 🔒 Autenticação (Protegidos)

| Método | Endpoint | Descrição | Permissão |
|--------|----------|-----------|-----------|
| `POST` | `/api/v1/auth/refresh` | Renovar token | Autenticado |
| `POST` | `/api/v1/auth/change-password` | Alterar senha | Autenticado |
| `GET` | `/api/v1/auth/me` | Dados do usuário logado | Autenticado |

### 👥 Usuários

| Método | Endpoint | Descrição | Permissão |
|--------|----------|-----------|-----------|
| `POST` | `/api/v1/users/` | Criar usuário | Admin |
| `GET` | `/api/v1/users/` | Listar todos | Admin |
| `GET` | `/api/v1/users/{user_id}` | Buscar por ID | Autenticado* |
| `PUT` | `/api/v1/users/{user_id}` | Atualizar | Autenticado* |
| `DELETE` | `/api/v1/users/{user_id}` | Deletar | Admin |

*Usuários comuns podem editar apenas seus próprios dados

### 💰 Transações

| Método | Endpoint | Descrição | Permissão |
|--------|----------|-----------|-----------|
| `POST` | `/api/v1/transactions/` | Criar transação | Autenticado |
| `GET` | `/api/v1/transactions/` | Listar transações | Autenticado |
| `POST` | `/api/v1/transactions/filter` | Filtrar transações | Autenticado |
| `GET` | `/api/v1/transactions/{id}` | Buscar por ID | Autenticado |
| `PUT` | `/api/v1/transactions/{id}` | Atualizar | Autenticado |
| `DELETE` | `/api/v1/transactions/{id}` | Deletar | Autenticado |
| `GET` | `/api/v1/transactions/summary` | Resumo | Autenticado |

### 📊 Relatórios

| Método | Endpoint | Descrição | Permissão |
|--------|----------|-----------|-----------|
| `GET` | `/api/v1/reports/monthly/{year}/{month}` | Relatório mensal | Autenticado |
| `GET` | `/api/v1/reports/yearly/{year}` | Relatório anual | Autenticado |
| `GET` | `/api/v1/reports/yearly-breakdown/{year}` | Breakdown anual | Autenticado |
| `GET` | `/api/v1/reports/highest-expenses` | Top 10 despesas | Autenticado |
| `GET` | `/api/v1/reports/spending-trend` | Tendência de gastos | Autenticado |
| `GET` | `/api/v1/reports/recurring-transactions` | Transações recorrentes | Autenticado |
| `GET` | `/api/v1/reports/health-check` | Saúde financeira | Autenticado |

---

## 🏗️ Estrutura do Projeto

```
finance-planner-api/
├── app/
│   ├── api/                    # Endpoints
│   │   ├── deps.py             # Dependências
│   │   └── v1/
│   │       ├── router.py       # Agregador de routers
│   │       └── endpoints/
│   │           ├── auth.py
│   │           ├── users.py
│   │           ├── transactions.py
│   │           └── reports.py
│   │
│   ├── core/                   # Configurações
│   │   ├── config.py
│   │   └── security.py
│   │
│   ├── db/                     # Banco de dados
│   │   ├── base.py
│   │   ├── base_class.py
│   │   ├── session.py
│   │   └── init_db.py
│   │
│   ├── models/                 # Models ORM
│   │   ├── user.py
│   │   └── transaction.py
│   │
│   ├── schemas/                # Schemas Pydantic
│   │   ├── response.py
│   │   ├── token.py
│   │   ├── user/
│   │   ├── transaction/
│   │   └── report/
│   │
│   ├── crud/                   # CRUD operations
│   │   ├── base.py
│   │   ├── user.py
│   │   └── transaction.py
│   │
│   ├── services/               # Business logic
│   │   ├── auth_service.py
│   │   └── finance_service.py
│   │
│   └── main.py                 # Entry point
│
├── alembic/                    # Migrations
├── .env                        # Variáveis de ambiente
├── .env.example                # Template .env
├── pyproject.toml              # Dependências
├── run.py                      # Script para rodar
└── README.md                   # Este arquivo
```

---

## 🔐 Autenticação & Segurança

### OAuth2 Password Flow

Esta API implementa o padrão **OAuth2 com Password Flow** e **JWT tokens**.

#### Fluxo de Autenticação

1. **Registro** → Criar conta com email e senha
2. **Login** → Receber `access_token` + `refresh_token`
3. **Usar Token** → Incluir em requisições protegidas
4. **Token Expira** → Usar `refresh_token` para novo `access_token`

#### Headers Obrigatórios

```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

#### Segurança Implementada

- ✅ Senhas hasheadas com **bcrypt** (12 rounds)
- ✅ Tokens JWT com **HMAC-SHA256**
- ✅ Access token expira em **30 minutos**
- ✅ Refresh token expira em **7 dias**
- ✅ Tokens rotacionados em cada refresh
- ✅ Validação de assinatura em todo request
- ✅ Controle de permissões (RBAC)
- ✅ Email validation

---

## 📦 Categorias de Transações

### 💸 Receitas (Income)
- `salary` - Salário
- `freelance` - Trabalho autônomo
- `investment` - Investimentos
- `business` - Negócio próprio
- `other_income` - Outras receitas

### 💸 Despesas (Expense)
- `food` - Alimentação
- `transport` - Transporte
- `housing` - Moradia
- `utilities` - Contas (luz, água, etc)
- `healthcare` - Saúde
- `education` - Educação
- `entertainment` - Lazer
- `shopping` - Compras
- `subscription` - Assinaturas
- `other_expense` - Outras despesas

---

## 🔧 Variáveis de Ambiente (.env)

```
# Projeto
PROJECT_NAME=Finance Planner API
VERSION=1.0.0
API_V1_STR=/api/v1

# Banco de Dados
DATABASE_URL=sqlite:///./finance.db

# Segurança
SECRET_KEY=sua-chave-secreta-muito-longa-e-aleatoria-aqui
ALGORITHM=HS256

# Tokens
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Admin Inicial (opcional)
FIRST_SUPERUSER_EMAIL=admin@example.com
FIRST_SUPERUSER_PASSWORD=admin123!@#
FIRST_SUPERUSER_NAME=Administrador
```

---

## 🗄️ Banco de Dados

### Schema

#### Tabela: users
```
id (INTEGER, PRIMARY KEY)
email (VARCHAR, UNIQUE, NOT NULL)
hashed_password (VARCHAR, NOT NULL)
full_name (VARCHAR)
is_active (BOOLEAN, DEFAULT TRUE)
is_superuser (BOOLEAN, DEFAULT FALSE)
created_at (DATETIME, DEFAULT NOW())
updated_at (DATETIME, ON UPDATE NOW())
```

#### Tabela: transactions
```
id (INTEGER, PRIMARY KEY)
user_id (INTEGER, FOREIGN KEY, NOT NULL)
type (ENUM: 'income', 'expense')
category (ENUM: 'salary', 'food', ...)
amount (FLOAT, NOT NULL)
description (VARCHAR)
date (DATETIME, NOT NULL)
is_recurring (BOOLEAN, DEFAULT FALSE)
created_at (DATETIME, DEFAULT NOW())
updated_at (DATETIME, ON UPDATE NOW())
```

### Migrations

```
# Criar nova migration
alembic revision --autogenerate -m "descrição da mudança"

# Aplicar migrations
alembic upgrade head

# Voltar migration
alembic downgrade -1
```

---

## 📚 Documentação

### Swagger UI
```
http://localhost:8000/docs
```

### ReDoc
```
http://localhost:8000/redoc
```

### OpenAPI JSON
```
http://localhost:8000/api/v1/openapi.json
```

---

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/minha-feature`)
3. Commit suas mudanças (`git commit -m 'Adiciona minha feature'`)
4. Push para a branch (`git push origin feature/minha-feature`)
5. Abra um Pull Request

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## 👨‍💻 Autor

**Gustavo Diego**
- GitHub: [@GustavoDiego](https://github.com/GustavoDiego)
- Email: gustavodiego298@gmail.com

---

## 🙏 Agradecimentos

- [FastAPI](https://fastapi.tiangolo.com/) - Web framework
- [SQLAlchemy](https://www.sqlalchemy.org/) - ORM
- [Pydantic](https://docs.pydantic.dev/) - Data validation
- [Alembic](https://alembic.sqlalchemy.org/) - Database migrations

---

## 📞 Suporte

Para suporte, envie um email para gustavodiego298@gmail.com ou abra uma issue no GitHub.

---

## 🔗 Links Úteis

- [Documentação FastAPI](https://fastapi.tiangolo.com/)
- [Documentação SQLAlchemy](https://docs.sqlalchemy.org/)
- [JWT.io](https://jwt.io/)
- [OAuth 2.0](https://oauth.net/2/)

---

**Desenvolvido com ❤️ usando FastAPI**


