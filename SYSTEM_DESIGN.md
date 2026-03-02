# System Design & Architecture: Syntivra Helpdesk

Este documento detalha o "The Why" por trás das decisões arquiteturais tomadas para garantir que o Syntivra seja um sistema **SaaS robusto, escalável e seguro**.

---

## 🏗️ 1. Estratégia de Isolamento Multi-Tenancy

Diferente de sistemas monousuário, o Syntivra foi desenhado para hospedar múltiplas organizações (tenants) no mesmo banco de dados.

### A Decisão: Shared Database / Shared Schema
Optamos por esta abordagem por ser a mais custo-efetiva e fácil de manter em escala (milhares de tenants). O isolamento é garantido na camada de aplicação (App-level Isolation).

### Implementação Técnica:
- **ContextVars (Python 3.7+):** Utilizamos variáveis de contexto para armazenar o `tenant_id` da requisição atual. Isso é "thread-safe" e garante que uma requisição nunca acesse dados de outra.
- **Custom Manager & Queryset:** Sobrescrevemos o método `get_queryset()` do `django.db.models.Manager`. Toda query disparada através do `TenantModel` é filtrada automaticamente:
  ```python
  # O Django injeta automaticamente:
  Ticket.objects.all() -> WHERE organization_id = CURRENT_TENANT_ID
  ```
- **Segurança Blindada:** O Middleware de autenticação garante que o `tenant_id` seja extraído diretamente de um **JWT assinado**, tornando o isolamento impossível de ser burlado por spoofing de ID.

---

## ⚡ 2. Arquitetura Baseada em Eventos (Signals)

Para manter as Views do Django rápidas e o código desacoplado, utilizamos o sistema de **Signals**.

### Fluxo de Criação de um Ticket:
1. **View:** Recebe o `POST` e valida via Serializer.
2. **Database:** Salva o registro básico.
3. **Signal `post_save`:** 
   - Dispara o **Audit Log** (Imutável).
   - Executa o **Service de Atribuição** (Assign Logic).
   - Aciona o **Pipeline de IA** (Procura resoluções similares).
   - Cria a primeira mensagem de boas-vindas da IA no Chat.

**Vantagem:** O usuário recebe a resposta de "Sucesso" em milissegundos, enquanto a inteligência do sistema trabalha nos bastidores.

---

## 🧠 3. Mecanismo de IA e Sugestões Cognitivas

O MVP implementado foca em **Busca por Similaridade Textual (Similarity Search)**.

### O Funcionamento:
- Quando um novo chamado é aberto, o `AIService` realiza uma busca por tickets com o status `RESOLVED` dentro da mesma organização.
- Atualmente, utilizamos o motor de busca textual do PostgreSQL, que é extremamente performático.
- **Preparado para o Futuro:** A estrutura de `AIService` é agnóstica. Para escalar, basta substituir a query de busca pelo `pgvector` e uma chamada à API da OpenAI/Anthropic para gerar os embeddings, sem mudar uma linha de lógica do chat ou da UI.

---

## 🎨 4. Design System & Frontend UX

O Frontend foi construído focando em **Affordance** e **Hierarquia Visual**.

- **Zustand (State Management):** Escolhemos Zustand ao invés de Redux pela sua simplicidade e performance. O estado de autenticação e do usuário é centralizado e persistente no `localStorage`.
- **Glassmorphism UI:** O uso de desfoque de fundo e bordas sutis não é apenas estético, mas ajuda a focar o técnico na tarefa central (o chat ou o gráfico), reduzindo a carga cognitiva.
- **Mobile-First Responsiveness:** O sistema é 100% responsivo, permitindo que técnicos acompanhem SLA de seus smartphones.

---

## 🛡️ 5. Segurança e RBAC

O controle de acesso é implementado em três camadas:
1. **Model Layer:** Isolamento de Tenant.
2. **API Layer (DRF Permissions):** Filtros baseados em Roles (`IsAdmin`, `IsTechnician`).
3. **UI Layer:** Oculção de menus e botões protegidos.

### Exemplo de Fluxo:
Um `END_USER` pode ver a lista de tickets (após autenticação), mas o Serializer impede que ele altere o campo `assigned_to` ou `assigned_by`, garantindo integridade total do banco.

---

Este projeto demonstra competência em **Design de Sistemas Distribuídos e SaaS Moderno**.
