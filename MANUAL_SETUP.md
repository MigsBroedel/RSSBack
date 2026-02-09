# Guia de Configuração: Backend Sem Docker (Cloud DB)

Este guia documenta o processo de configurar e rodar o backend do "Personalized RSS Feed" sem utilizar Docker, conectando-se diretamente a um banco de dados na nuvem (ex: Supabase) e Redis.

## 1. Visão Geral das Mudanças
Para simplificar o deploy e o desenvolvimento local, removemos a dependência do Docker.
- **Removido**: `Dockerfile`, `docker-compose.yml`.
- **Alterado**: `render.yaml` para não provisionar banco gerenciado, mas sim aceitar uma `DATABASE_URL` externa.
- **Novo Fluxo**: Uso de ambiente virtual Python (`venv`) e serviços externos.

## 2. Pré-requisitos
- **Python 3.11+**
- **Redis**: Instância local ou na nuvem (ex: Upstash ou Render Redis).
- **Banco de Dados PostgreSQL**: Instância na nuvem (ex: Supabase).

## 3. Configuração do Banco de Dados (Supabase)
1. Crie um projeto no [Supabase](https://supabase.com/).
2. Vá em `Project Settings` -> `Database`.
3. Em `Connection string`, selecione `URI` e copie a string.
   - **Nota**: Se estiver em um ambiente Transactional (como Serverless functions), use a porta 6543 e o pooler. Para servidores long-running como este backend, a conexão direta (porta 5432) é preferível.
   - Formato: `postgresql+asyncpg://postgres:[SUA-SENHA]@db.[REF-DO-PROJETO].supabase.co:5432/postgres`
   - **Importante**: Certifique-se de que o driver seja compatível. No código (`app/core/config.py`), nós já tratamos automaticamente a conversão de `postgres://` para `postgresql+asyncpg://`.

## 4. Configuração Local

### Passo 1: Limpeza (Se aplicável)
Se você veio da versão Docker, remova os arquivos antigos:
```bash
rm Dockerfile docker-compose.yml
```

### Passo 2: Variáveis de Ambiente
Copie o exemplo e configure:
```bash
cp .env.example .env
```
Edite o arquivo `.env`:
```ini
# Conexão com Supabase
DATABASE_URL="postgresql+asyncpg://postgres:senha@db.ref.supabase.co:5432/postgres"

# Conexão com Redis (Local ou Cloud)
REDIS_URL="redis://localhost:6379/0"

# Outras configs
SECRET_KEY="sua_chave_secreta_aqui"
```

### Passo 3: Instalação de Dependências
Crie e ative o ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
# .\venv\Scripts\activate  # Windows
```

Instale os pacotes:
```bash
pip install -r requirements.txt
```

### Passo 4: Migrações
Com o `.env` configurado apontando para o Supabase, rode as migrações para criar as tabelas lá:
```bash
alembic upgrade head
```

### Passo 5: Rodando a Aplicação
**API (Servidor Web):**
```bash
uvicorn app.main:app --reload
```

**Worker (Celery):**
Em um terminal separado (com venv ativado):
```bash
celery -A app.workers.celery_app worker --loglevel=info
```

## 5. Deploy (Render.com)
O arquivo `render.yaml` foi ajustado para este novo modelo.

### Ao criar o Blueprint no Render:
1. O Render vai ler o `render.yaml`.
2. Ele criará o **Web Service** e o **Worker**.
3. **Redis**: Ele ainda criará um Redis interno (free) para comunicação entre API e Worker.
4. **Banco de Dados**: Ao contrário de antes, ele **NÃO** criará um banco gerenciado.
   - Você precisará ir no Dashboard do Render, selecionar os serviços (`rss-backend` e `rss-worker`) e adicionar a variável de ambiente `DATABASE_URL` manualmente com a string de conexão do Supabase.

Isso garante um deploy mais barato (sem pagar pelo banco gerenciado do Render) e flexível.
