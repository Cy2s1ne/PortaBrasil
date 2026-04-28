# PortaBrasil — Sistema de Gerenciamento de Despachância Aduaneira Brasileira

> Uma plataforma web full-stack para gerenciamento de operações de despachância aduaneira brasileira, incluindo análise de documentos PDF, rastreamento de processo de liberação em 10 etapas, análise de custos e auditoria auxiliada por IA e revisão financeira.

---

## Índice

- [Visão Geral](#visão-geral)
- [Arquitetura](#arquitetura)
- [Stack Tecnológico](#stack-tecnológico)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Funcionalidades](#funcionalidades)
- [Início Rápido](#início-rápido)
  - [Pré-requisitos](#pré-requisitos)
  - [Configuração do Backend](#configuração-do-backend)
  - [Configuração do Frontend](#configuração-do-frontend)
- [Configuração](#configuração)
- [Banco de Dados](#banco-de-dados)
- [Referência da API](#referência-da-api)
- [Guia do Usuário](#guia-do-usuário)
- [Módulos do Sistema](#módulos-do-sistema)
- [Segurança](#segurança)
- [Desenvolvimento](#desenvolvimento)

---

## Visão Geral

**PortaBrasil** é uma plataforma web full-stack para gerenciamento de **operações de despachância aduaneira brasileira**. Digitaliza todo o fluxo de liberação aduaneira — desde o upload de documentos PDF brutos (conhecimentos de embarque, faturas, declarações aduaneiras) passando pela extração de dados assistida por IA, análise de custos financeiros, até o ciclo completo de vida de 10 etapas do processo de liberação aduaneira.

Público-alvo: empresas de logística, despachantes aduaneiros e transitários.

---

## Arquitetura

```
┌─────────────────────────────────────────────────────────┐
│              Navegador (React SPA)                      │
│  http://localhost:5173                                  │
└─────────────────────┬───────────────────────────────────┘
                      │ HTTP / REST API (JSON)
┌─────────────────────▼───────────────────────────────────┐
│              Backend Flask                              │
│  http://localhost:5001 /api/*                           │
│  ┌──────────┬───────────┬───────────┬─────────────┐    │
│  │ Autent.  │ Análise  │ Negócio & │ Auditoria & │    │
│  │          │ PDF      │ Custo     │ Rev.Finan.  │    │
│  └──────────┴───────────┴───────────┴─────────────┘    │
└─────────────────────┬───────────────────────────────────┘
                      │ SQL
┌─────────────────────▼───────────────────────────────────┐
│         MySQL 8.x  (produção)                          │
│         SQLite      (desenvolvimento, auto-criado)       │
└─────────────────────────────────────────────────────────┘
```

---

## Stack Tecnológico

| Camada | Tecnologia |
|---|---|
| **Frontend** | React 19, Vite 7, Tailwind CSS 3, Lucide React |
| **Backend** | Python 3.11+, Flask 3, Flask-CORS |
| **Autenticação** | JWT (PyJWT), hash de senha SHA-256 |
| **Banco de Dados** | MySQL 8.x (produção) / SQLite (desenvolvimento) |
| **IA - Parsing** | Zhipu AI (ZAI SDK) — análise de documentos PDF |
| **IA - Revisão** | Zhipu AI (ZAI SDK) — auditoria e análise financeira |
| **ORM** | SQL estilo SQLAlchemy (pymysql / sqlite3) |
| **Taxas de Câmbio** | API Open Exchange Rates (fallback: taxas em cache) |

---

## Estrutura do Projeto

```
PortaBrasil/
├── Portabrasil-server/           # Backend Flask
│   ├── main.py                   # Ponto de entrada
│   ├── app/
│   │   ├── factory.py            # Factory da app (CORS, erros, blueprints)
│   │   ├── core/
│   │   │   ├── auth.py           # JWT, hash, decorator de autenticação
│   │   │   └── responses.py      # Auxiliares de resposta JSON
│   │   └── routes/
│   │       ├── health.py          # GET /api/health
│   │       ├── auth.py           # Login / registro / esqueci senha / usuários
│   │       ├── files.py          # Upload PDF e gatilhos de análise
│   │       ├── documents.py      # Ingestão de texto bruto
│   │       ├── business.py       # CRUD de registros e consulta de taxas
│   │       ├── tasks.py          # Status de tarefa de análise
│   │       ├── dashboard.py      # Estatísticas da página inicial
│   │       ├── process.py        # Rastreamento de 10 etapas
│   │       ├── reports.py        # Registros de relatórios
│   │       ├── cost.py           # Análise de custos e câmbio
│   │       ├── ai_review.py      # Auditoria IA e revisão financeira
│   │       └── admin.py          # Gerenciamento de usuários
│   ├── database.py               # Conexão BD e esquema SQLite
│   ├── services.py              # Serviços de lógica de negócio
│   ├── pdf_parser.py            # Parser de PDF via Zhipu AI
│   ├── parser_rules.py           # Regras regex para extração
│   ├── sql/                        # Diretório do esquema SQL
│   └── instance/                 # SQLite DB auto-criado aqui
│
├── Portabrasil-web/
│   └── customs-dashboard/        # Frontend React
│       ├── src/
│       │   ├── App.jsx           # Shell principal (sidebar, header)
│       │   ├── LoginPage.jsx    # Página de login
│       │   ├── views/
│       │   │   ├── HomeView.jsx           # Visão geral do painel
│       │   │   ├── UploadView.jsx         # Upload de PDF
│       │   │   ├── ProcessTrackingView.jsx # Rastreamento de 10 etapas
│       │   │   ├── CostAnalysisView.jsx   # Cálculo e registros de custo
│       │   │   ├── ReportView.jsx         # Centro de relatórios
│       │   │   └── AdminManagementView.jsx # Gerenciamento de usuários
│       │   ├── components/navigation/
│       │   │   └── SidebarItem.jsx
│       │   └── shared/
│       │       ├── auth/storage.js   # Armazenamento JWT
│       │       ├── config/api.js     # URL base da API
│       │       ├── i18n/
│       │       │   ├── translations.js      # Traduções da UI (zh/en/pt)
│       │       │   └── language-context.jsx
│       │       └── utils/
│       │           ├── http.js    # Auxiliar fetch autenticado
│       │           └── format.js  # Formatadores de número/moeda
│       └── package.json
│
├── portabrasil.sql                # Dump completo do esquema MySQL
└── docs/
    ├── README.md                 # Versão em inglês
    ├── README_zh.md              # Versão em chinês
    └── 系统模块流程图.md          # Diagramas de fluxo (Mermaid)
```

---

## Funcionalidades

### 1. Autenticação e Autorização
- Autenticação baseada em JWT (token de acesso, expiração de 120 minutos)
- 5 funções: **Super Admin**, **Admin**, **Despachante**, **Operador Aduaneiro**, **Financeiro**
- Controle de acesso baseado em função (RBAC) em todos os endpoints protegidos
- Hash de senha SHA-256 (com atualização automática de senhas legadas no login)
- Registro de usuário, recuperação de senha

### 2. Upload e Análise de Documentos PDF
- Upload de arquivos PDF (máx. 25 MB) com deduplicação via hash SHA-256
- Análise orientada por IA via Zhipu AI (tipos: LLM / OCR / RULE)
- Polling assíncrono do status da tarefa de análise
- Upsert por S/Ref — re-envio do mesmo documento atualiza registros existentes
- Endpoint de ingestão de texto bruto para entrada direta de texto

### 3. Extração de Dados de Negócios
Extraídos de PDFs analisados: S/Ref, N/Ref, Nº da Fatura, Nº da NF, dados do cliente (nome, endereço, cidade, estado, CNPJ/CPF), documentos de transporte (MAWB/MBL, HAWB/HBL), datas-chave (registro, chegada, liberação, carregamento), informações de carga (peso, volume, descrição), dados financeiros (frete, FOB, CIF, CIF-BRL, taxas de câmbio) e até 50 itens de taxa por registro.

### 4. Processo de Liberação Aduaneira em 10 Etapas
- Cada Conhecimento de Embarque (BL) mapeia um registro de processo
- 10 etapas sequenciais por processo: PENDENTE / CONCLUÍDO
- Derivação automática do status geral: todas completas → **LIBERADO** | etapa 6+ completa → **EM VISTORIA** | demais → **EM PROCESSO**
- Status da etapa, hora de conclusão e descrição editáveis

### 5. Análise de Custos
- Entrada: taxa aduaneira, reembolso, valor em USD, taxa de câmbio, outras taxas, quantidade
- Calculado: taxa aduaneira líquida, conversão USD→BRL, custo total, custo por unidade
- Busca de taxa USD/BRL em tempo real com cache no banco de dados e fallback
- Salvar registros de cálculo no histórico com detalhamento por produto
- Revisão de saúde financeira por IA com verificações baseadas em regras

### 6. Auditoria de IA e Revisão Financeira
- **Auditoria de Negócios** (`POST /api/ai-review/business/:id/run`): consistência de débito/crédito, consistência de resumo de taxas, completude de campos, detecção de anomalia de reembolso
- **Revisão Financeira** (`POST /api/ai-review/cost-record/:id/review`): validade da quantidade total, razoabilidade da taxa de câmbio, razão reembolso/taxa aduaneira, positividade do custo por unidade
- Resultados: nível de risco/saúde, pontuação, descobertas com severidade, evidências, sugestões

### 7. Painel e Relatórios
- Página inicial: total de registros, distribuição por status, total de impostos, kanban de etapas, feed de atividades recentes
- Centro de relatórios: lista filtrável/pesquisável de todos os registros de liberação

### 8. Internacionalização
- UI disponível em: **Chinês Simplificado (zh)**, **Inglês (en)**, **Português (pt)**
- Trocador de idioma na barra de ferramentas do cabeçalho

---

## Início Rápido

### Pré-requisitos
- **Python** 3.11+, **Node.js** 18+, **npm**
- (Opcional) **MySQL 8.x** — SQLite usado automaticamente se não configurado
- (Opcional) **Zhipu AI API Key** — necessário apenas para análise de PDF e revisão de IA

### Configuração do Backend

```bash
cd PortaBrasil/Portabrasil-server
uv sync

# Opcional: definir variáveis de ambiente
export DATABASE_URL='mysql://root:password@127.0.0.1:3306/portabrasil?charset=utf8mb4'
export ZHIPU_API_KEY='your-zhipu-api-key'
export JWT_SECRET='your-long-random-secret-here'

# MySQL: inicializar banco de dados
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS portabrasil DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
mysql -u root -p portabrasil < ../portabrasil.sql

# Iniciar servidor
uv run flask --app main run --host 0.0.0.0 --port 5001 --debug
```

> Sem `DATABASE_URL`, o servidor usa SQLite automaticamente (`instance/portabrasil.db`).

**Credenciais padrão**: `admin` / `admin123456`

### Configuração do Frontend

```bash
cd PortaBrasil/Portabrasil-web/customs-dashboard
npm install
npm run dev
```

Frontend em `http://localhost:5173`, faz proxy da API para `http://localhost:5001`.

---

## Configuração

### Variáveis de Ambiente (Backend)

| Variável | Padrão | Descrição |
|---|---|---|
| `DATABASE_URL` | SQLite (`instance/portabrasil.db`) | String de conexão MySQL |
| `ZHIPU_API_KEY` | — | Chave API Zhipu AI para análise de PDF |
| `JWT_SECRET` | `change-this-in-production...` | Chave secreta para assinatura JWT |
| `JWT_EXPIRES_MINUTES` | `120` | Expiração do token em minutos |
| `UPLOAD_DIR` | `./uploads` | Diretório de armazenamento dos PDFs |
| `DEFAULT_REGISTER_ROLE` | `FORWARDER` | Função para novos registros |

### Variáveis de Ambiente (Frontend)

| Variável | Padrão | Descrição |
|---|---|---|
| `VITE_API_BASE_URL` | `http://127.0.0.1:5001` | URL base da API do backend |

---

## Banco de Dados

| Ambiente | Engine | Fonte do Esquema |
|---|---|---|
| Produção | MySQL 8.x | `portabrasil.sql` (dump completo) |
| Desenvolvimento | SQLite | Auto-criado por `database.py` |

**Migrações incrementais MySQL** (não são mais necessárias, todas as tabelas estão em `portabrasil.sql`):
```bash
# Todas as tabelas estão em portabrasil.sql. Para banco existente, basta reimportar:
mysql -u root -p portabrasil < ../../portabrasil.sql
```

**Tabelas principais**: `pdf_file`, `pdf_parse_task`, `customs_business`, `customs_business_fee_item`, `users`, `roles`, `user_role`, `customs_process_record`, `customs_process_step`, `customs_activity`, `fx_rate_cache`, `customs_cost_record`, `customs_cost_item`, `ai_audit_run`, `ai_audit_finding`, `ai_finance_review`, `ai_finance_item`

> Nota: `statement_summary` e `statement_summary_item` existem apenas no esquema MySQL.

---

## Referência da API

### Públicos (Sem Autenticação)
| Método | Caminho | Descrição |
|---|---|---|
| `GET` | `/api/health` | Verificação de saúde |
| `POST` | `/api/auth/login` | Login (retorna JWT) |
| `POST` | `/api/auth/register` | Registrar novo usuário |
| `POST` | `/api/auth/forgot-password` | Redefinir senha |

### Painel e Processo
| Método | Caminho | Descrição |
|---|---|---|
| `GET` | `/api/dashboard/overview` | Estatísticas da página inicial |
| `GET` | `/api/process/records` | Listar registros de liberação |
| `GET` | `/api/process/records/{id}` | Obter detalhes do registro |
| `PUT` | `/api/process/records/{id}/steps/{no}` | Atualizar status da etapa |
| `GET` | `/api/reports/records` | Registros de relatórios |

### Negócio e Arquivos
| Método | Caminho | Descrição |
|---|---|---|
| `POST` | `/api/files/upload` | Upload de PDF (multipart) |
| `GET` | `/api/files` | Listar arquivos |
| `GET` | `/api/files/{id}` | Obter detalhes do arquivo |
| `POST` | `/api/files/{id}/parse` | Disparar análise |
| `GET` | `/api/tasks/{id}` | Obter status da tarefa |
| `POST` | `/api/documents/from-text` | Ingestão de texto bruto |
| `GET` | `/api/business` | Pesquisar registros de negócio |
| `GET` | `/api/business/{id}` | Obter registro de negócio |
| `GET` | `/api/business/{id}/fees` | Obter itens de taxa |

### Análise de Custos
| Método | Caminho | Descrição |
|---|---|---|
| `GET` | `/api/cost/overview` | Visão geral de custos |
| `GET` | `/api/cost/exchange-rate` | Obter taxa de câmbio |
| `POST` | `/api/cost/calculate` | Calcular custo |
| `POST` | `/api/cost/records` | Salvar registro de custo |
| `GET` | `/api/cost/records` | Listar registros de custo |
| `GET` | `/api/cost/records/{id}` | Obter detalhes do registro de custo |

### Revisão de IA
| Método | Caminho | Descrição |
|---|---|---|
| `POST` | `/api/ai-review/business/{id}/run` | Executar auditoria de negócio |
| `GET` | `/api/ai-review/audit/runs` | Listar execuções de auditoria |
| `GET` | `/api/ai-review/audit/runs/{id}` | Obter detalhes da auditoria |
| `POST` | `/api/ai-review/cost-record/{id}/review` | Executar revisão financeira |
| `GET` | `/api/ai-review/finance/reviews` | Listar revisões financeiras |

### Admin
| Método | Caminho | Descrição |
|---|---|---|
| `GET` | `/api/auth/me` | Obter usuário atual |
| `POST` | `/api/auth/users` | Criar usuário (admin only) |
| `PUT` | `/api/auth/users/{id}` | Atualizar usuário (admin only) |
| `PUT` | `/api/auth/users/{id}/password` | Redefinir senha (admin only) |
| `PUT` | `/api/auth/users/{id}/status` | Ativar/desativar usuário (admin only) |

---

## Guia do Usuário

### Fazer Login
1. Abra `http://localhost:5173`
2. Digite `admin` / `admin123456`
3. Alterne o idioma com o botão **ZH / EN / PT** no canto superior direito

### Upload de Documento
1. Clique em **Upload** na barra lateral
2. Selecione um arquivo PDF
3. Escolha **Upload & Parse** ou **Upload Only**
4. Para **Upload & Parse**: aguarde ~10–30 segundos para conclusão

### Rastreamento do Processo de Liberação
1. Clique em **Process** na barra lateral
2. Navegue pela lista de registros (filtrável por nº BL, status)
3. Clique em um registro → kanban de 10 etapas mostra PENDENTE/CONCLUÍDO
4. Clique em **Edit** em uma etapa → defina status + data de conclusão → Save
5. Status geral deriva automaticamente: EM PROCESSO → EM VISTORIA → LIBERADO

### Análise de Custos
1. Clique em **Cost** na barra lateral
2. Insira: taxa aduaneira, reembolso, valor em USD, taxa de câmbio, outras taxas, quantidade
3. Clique em **Calculate** → veja taxa líquida, conversão BRL, custo total/unitário
4. Clique em **Save Record** para persistir no histórico

### Auditoria de IA
1. Abra detalhes de um registro de negócio ou custo
2. Clique em **AI Audit** ou **Finance Review**
3. Resultados: nível de risco/saúde, pontuação, descobertas com severidade, evidências, sugestões

### Admin
1. Clique em **Admin** (visível apenas para SUPER_ADMIN e ADMIN)
2. Gerencie usuários: criar, atualizar, desativar, redefinir senhas, atribuir funções

---

## Módulos do Sistema

9 módulos funcionais. Veja `docs/系统模块流程图.md` para diagramas de fluxo Mermaid:

| # | Módulo | Descrição |
|---|---|---|
| 1 | Autenticação | Autenticação JWT, RBAC com 5 funções |
| 2 | Upload de Documentos | Upload de PDF, deduplicação SHA-256 |
| 3 | Análise de Documentos | Análise de PDF via Zhipu AI, extração de campos |
| 4 | Auditoria e Revisão | Auditoria de negócios por IA + revisão financeira |
| 5 | Contabilidade de Custos | Cálculo de custos com conversão de câmbio |
| 6 | Rastreamento de Processo | Ciclo de vida de 10 etapas de liberação |
| 7 | Gerenciamento de Tarefas | Rastreamento assíncrono de tarefas de análise |
| 8 | Painel Estatístico | Kanban da página inicial, feed de atividades |
| 9 | Administração do Sistema | CRUD de usuários, atribuição de funções |

---

## Segurança

- **Tokens JWT Bearer** em todos os endpoints protegidos
- **Hash de senha**: SHA-256 com atualização automática de senhas legadas
- **CORS**: aberto em desenvolvimento; restringir em produção
- **Injeção SQL**: todas as consultas usam instruções parametrizadas
- **Proteção SUPER_ADMIN**: contas super admin não podem ser modificadas/desativadas via API
- **Prevenção de auto-desativação**: usuários não podem desativar sua própria conta
- **Prevenção de escalação de função**: não-super-admins não podem atribuir a função SUPER_ADMIN

---

## Desenvolvimento

### Adicionar Nova Rota
1. Crie `app/routes/my_resource.py`
2. Registre em `app/factory.py`:
   ```python
   from app.routes.my_resource import bp as my_resource_bp
   app.register_blueprint(my_resource_bp, url_prefix='/api/my-resource')
   ```
3. Use `@jwt_required` para rotas protegidas e `api_response()` para respostas JSON

### Adicionar Nova View
1. Crie `src/views/MyView.jsx`
2. Exporte de `src/views/index.js`
3. Adicione em `menuItems` e no `switch renderContent()` em `App.jsx`

### Executar Testes
1. `cd Portabrasil-server && uv run flask --app main run --port 5001 --debug`
2. `cd Portabrasil-web/customs-dashboard && npm run dev`
3. Abra `http://localhost:5173`

---

*PortaBrasil — Simplificando as Operações Aduaneiras Brasileiras.*
