# Tech Challenge - Fast Food Self-Service

Este projeto faz parte de um **Tech Challenge**, que envolve a criação de um sistema de autoatendimento para uma lanchonete em expansão. A ideia é permitir que os clientes façam pedidos de forma rápida e prática, enquanto o estabelecimento consegue gerenciar de forma eficiente produtos, clientes e pedidos.

---

## Visão Geral do Problema

A lanchonete está crescendo rapidamente, mas sem um **sistema de controle de pedidos**, o atendimento pode se tornar confuso e ineficiente:

- Risco de erros ao anotar manualmente os pedidos
- Perda de tempo com pedidos confusos ou esquecidos
- Clientes insatisfeitos devido a atrasos e falhas de comunicação

Para resolver esse problema, o projeto propõe um **sistema de autoatendimento** com as seguintes etapas:

1. **Pedido**
   - Cliente pode se identificar (CPF, nome, e-mail) ou permanecer anônimo
   - Montagem do combo (lanche, acompanhamento, bebida e sobremesa – todos opcionais)
   - Exibição de nome, descrição e preço de cada produto

2. **Pagamento**
   - Integração de pagamento via QRCode do Mercado Pago (MVP)

3. **Acompanhamento**
   - Monitor para o cliente acompanhar o progresso do pedido (Recebido → Em preparação → Pronto → Finalizado)

4. **Entrega**
   - Notificação de pedido pronto para retirada
   - Ao retirar, o pedido é marcado como Finalizado

Além disso, o **acesso administrativo** permite:
- Gerenciar clientes (para campanhas promocionais)
- Gerenciar produtos (nome, categoria, preço, descrição e imagens)
- Acompanhar pedidos em andamento (tempo de espera, status, etc.)

---

## Estrutura do Projeto

- **`main.py`**: Ponto de entrada da aplicação (FastAPI).
- **`database.py`**: Configuração do banco de dados (engine, sessões).
- **`models.py`**: Modelos SQLAlchemy que representam as tabelas (e.g. `Product`, `User`).
- **`migrations/`**: Diretório gerado pelo **Alembic** para versionar e aplicar alterações no schema do banco de dados.
- **`docker-compose.yaml`**: Define os serviços do projeto (app + Postgres) para rodar em contêineres.
- **`Dockerfile`**: Define como construir a imagem Docker do aplicativo (base Python + pacotes).

---

## Configuração com Docker (Obrigatório)

Este projeto **requer** que você rode a aplicação e o banco de dados via **Docker e Docker Compose**. Dessa forma, todos terão um ambiente padrão e consistente.

### 1. Pré-requisitos

- **Docker** instalado ([Download Docker](https://www.docker.com/products/docker-desktop/))
- **Docker Compose** (geralmente incluso no Docker Desktop ou no pacote docker-cli em Linux)

### 2. Arquivo `.env`

Crie um arquivo `.env` na raiz do projeto com as variáveis de ambiente do banco e outras que precisar, por exemplo:

```
DB_HOST=db
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=mysecretpassword
DB_NAME=fastfood
```

O Docker Compose lê esse arquivo e injeta as variáveis nos contêineres.

### 3. Subir os Contêineres

Na raiz do projeto, rode:
```bash
docker compose up --build
```
Isso vai:
- **Construir** a imagem do aplicativo FastAPI
- Iniciar o contêiner **web** (FastAPI/Uvicorn) e o contêiner **db** (Postgres)
- Mapear as portas definidas no `docker-compose.yaml`
- Carregar as variáveis de ambiente do `.env`

### 4. Verificar a Aplicação

Abra [http://localhost:8000](http://localhost:8000) para acessar a aplicação.
A documentação automática (Swagger) estará em [http://localhost:8000/docs](http://localhost:8000/docs).

> **Observação**: Se você tiver um Postgres local rodando na porta 5432, pode ocorrer conflito. Ajuste a porta no `docker-compose.yaml`, por exemplo `5433:5432`, e mantenha `DB_PORT=5432` para o contêiner.

---

## Como Utilizar o Alembic (Migrações)

O **Alembic** é a ferramenta de migração do SQLAlchemy que permite versionar alterações no schema do banco de dados.

1. **Criar/Revisar Migrações**:
   ```bash
   docker compose run web alembic revision --autogenerate -m "Descrição da mudança"
   ```
   Isso executa o contêiner `web` e gera um script de migração em `migrations/versions/`.

2. **Aplicar Migrações**:
   ```bash
   docker compose run web alembic upgrade head
   ```
   Assim, o banco de dados no contêiner `db` refletirá as últimas alterações de schema.

3. **Exemplo de Reversão** (se precisar voltar uma migração):
   ```bash
   docker compose run web alembic downgrade -1
   ```

### Observações Importantes

- **Não** use `Base.metadata.create_all(bind=engine)` no código para criar ou atualizar tabelas. Essa responsabilidade é do Alembic.
- Se estiver usando `.env`, certifique-se de que as variáveis (como `DB_HOST`, `DB_PORT`, etc.) estão **alinhadas** com o `env.py` do Alembic (ou você pode sobrescrevê-las via `config.set_main_option("sqlalchemy.url", ...)`).

---

## Resumo

1. **Clonar** o repositório e criar o arquivo `.env` com as credenciais do BD.
2. Rodar `docker compose up --build` para subir o app (FastAPI) e o banco (Postgres).
3. **Gerenciar** o schema do banco via Alembic:
   - Criar migrações: `docker compose run web alembic revision --autogenerate -m "<msg>"`
   - Aplicar migrações: `docker compose run web alembic upgrade head`
4. **Acessar** a aplicação em [http://localhost:8000](http://localhost:8000) e conferir a documentação em [http://localhost:8000/docs](http://localhost:8000/docs).

Com isso, você terá o sistema de autoatendimento de Fast Food **padronizado** em contêineres Docker, pronto para evoluir e atender às necessidades do desafio.