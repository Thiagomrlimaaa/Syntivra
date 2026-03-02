# Syntivra: Enterprise SaaS Multi-Tenant Helpdesk (AI-Powered)

![Syntivra Header](https://raw.githubusercontent.com/lucide-react/lucide/main/icons/shield-check.svg) 
*A modern, scalable, and intelligent helpdesk platform for multi-company operations.*

---

## 🚀 Visão Geral
**Syntivra** é um SaaS (Software as a Service) de suporte técnico projetado para alta escalabilidade e isolamento total de dados entre clientes (Multi-tenancy). O sistema utiliza inteligência artificial para analisar tickets históricos e sugerir resoluções em tempo real, otimizando o tempo médio de resposta (MTTR) das equipes técnicas.

## 📸 Demonstração Visual

<table>
  <tr>
    <td><img src="screenshots/login.png" alt="Login Page" width="100%"></td>
    <td><img src="screenshots/dashboard.png" alt="Dashboard" width="100%"></td>
  </tr>
  <tr>
    <td><img src="screenshots/tickets.png" alt="Ticket List" width="100%"></td>
    <td><img src="screenshots/detail.png" alt="Ticket Detail" width="100%"></td>
  </tr>
</table>

---

## 🧠 Inteligência Artificial & Valor de Negócio

O grande diferencial do **Syntivra** não é apenas gerenciar chamados, mas transformar o suporte técnico em uma operação estratégica guiada por dados.

### Por que a I.A. é fundamental?
1.  **Redução Crítica de MTTR (Tempo Médio de Atendimento):** Ao analisar tickets resolvidos anteriormente, a I.A. sugere respostas precisas para problemas recorrentes. O técnico não perde tempo pesquisando em manuais; a solução "aparece" na tela.
2.  **Consistência nas Respostas:** Garante que diferentes técnicos forneçam a mesma qualidade de solução, mantendo o padrão de atendimento da empresa.
3.  **Memória Institucional:** Conforme técnicos seniores resolvem problemas complexos, a I.A. aprende. Se um sênior sair da empresa, o conhecimento permanece no sistema para auxiliar os novos colaboradores.

## 📈 Impacto no Dia a Dia da Empresa

O **Syntivra** foi desenhado para eliminar os gargalos comuns de grandes empresas:

- **Para o Gestor:** Dashboard em tempo real que mostra exatamente onde o suporte está travado (Gaps de Treinamento). Se 80% dos chamados são sobre um módulo específico, o gestor sabe que precisa treinar a equipe ou melhorar o software nesse ponto.
- **Para o Técnico:** Fila organizada por prioridade crítica e sugestões inteligentes que reduzem a carga mental e o estresse operacional.
- **Para o Cliente Final:** Respostas mais rápidas, acompanhamento transparente do status do chamado e a sensação de um suporte profissional e ágil.

---

## 🛠️ Stack Tecnológica (Senior Level)
- **Backend:** Python 3.12 / Django / Django REST Framework (DRF)
- **Database:** PostgreSQL (Ideal para produção) / SQLite (Dev)
- **Isolamento de Dados:** Custom Middleware + ContextVar Tenant Filtering
- **Inteligência Artificial:** PostgreSQL Full-Text Search (MVP) preparado para Vector Embeddings (pgvector)
- **Frontend:** React 18 / Vite / Tailwind CSS (Design Premium/Glassmorphism)
- **Data Viz:** Recharts para Dashboards de Performance
- **State Management:** Zustand (Store-based JWT Auth)
- **Infraestrutura:** Docker & Docker Compose (Containerized Ecosystem)

---

## 🏗️ Arquitetura & Decisões de Design

### 1. Multi-tenancy Nativo (Isolamento por Linha)
O sistema implementa uma estratégia de **Shared Database, Shared Schema**, isolando os dados através de um `organization_id` em cada tabela.
- **Isolamento Transparente:** Desenvolvemos um `TenantModel` e um `TenantManager` customizado que injeta automaticamente filtros de organização em todas as queries. O desenvolvedor não precisa se preocupar em esquecer o `filter(organization=...)`.
- **Segurança via Middleware:** Um middleware extrai o ID da organização do JWT e o injeta em uma `ContextVar` segura por thread/request.

### 2. Service Layer & Desacoplamento
Diferente de projetos básicos que colocam lógica nos models ou views, o Syntivra utiliza a **Service Layer Pattern**:
- **TicketService:** Gerencia a lógica de atribuição inteligente (Least-Assigned Strategy).
- **AIService:** Encapsula a lógica de busca semântica e sugestões.
- **Signals (Event-Driven):** Utilizamos Django Signals para disparar logs de auditoria e análises de IA de forma assíncrona, mantendo as Views limpas e rápidas.

### 3. RBAC (Role-Based Access Control)
Hierarquia de permissões robusta:
- **ADMIN:** Gestão total da organização e usuários.
- **TECHNICIAN:** Acesso à fila de atendimento, chat técnico e métricas de produtividade.
- **END_USER:** Abertura e acompanhamento de seus próprios chamados.

---

## 📊 Dashboard & Métricas Enterprise
O sistema foca em **Data-Driven Support**:
- **MTTR (Mean Time To Resolution):** Cálculo dinâmico direto no banco para medir eficiência.
- **Technician Productivity:** Gráficos de área mostrando volumetria de resoluções por especialista.
- **IA Conversation Analytics:** Insights sobre quanto a IA está contribuindo para as respostas.

---

## 🚦 Como Rodar o Projeto

### Modo Docker (Recomendado)
```bash
docker-compose up --build
```

### Configuração Manual (Backend)
1. `cd backend`
2. `python -m venv venv`
3. `.\venv\Scripts\activate` ou `source venv/bin/activate`
4. `pip install -r requirements.txt`
5. `python manage.py migrate`
6. `python manage.py runserver`

### Configuração Manual (Frontend)
1. `cd frontend`
2. `npm install`
3. `npm run dev`

---

## 🔑 Credenciais de Acesso (Teste)

Para testar as funcionalidades do sistema, utilize as seguintes contas padrão:

### 💎 Admin da Organização (Empresa Demo)
- **Email:** `admin@demo.com`
- **Senha:** `admin123`
- **Acesso:** Dashboard completo, gestão de usuários, configurações de IA e todos os tickets.

### 👤 Cliente / Usuário Final
- **Email:** `cliente@demo.com`
- **Senha:** `cliente123`
- **Acesso:** Portal do cliente, abertura de tickets e acompanhamento.

---

## 🔮 Roadmap de Evolução
- [ ] **Evolução de IA:** Substituição do Full-Text Search por **Vector Embeddings** utilizando `pgvector` e OpenAI/Mistral.
- [ ] **Billing Engine:** Integração com Stripe para faturamento por assento (per-seat) ou volumetria de tickets.
- [ ] **Realtime:** Migração do polling de chat para **WebSockets** (Django Channels).
- [ ] **Observabilidade:** Implementação de Prometheus e Grafana para monitoramento de saúde do sistema.

---

**Desenvolvido como projeto de portfólio de alto nível para Engenharia de Software.**
