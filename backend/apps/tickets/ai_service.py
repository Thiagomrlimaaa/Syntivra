"""
AIService — Motor de sugestões de resolução do Syntivra OS
-----------------------------------------------------------------
Estratégia em camadas:
  1. Busca por similaridade textual em tickets RESOLVIDOS do mesmo tenant (histórico)
  2. Fallback por categoria semântica (para novos tenants sem histórico)
  3. Fallback genérico profissional

Preparado para futura integração com pgvector + embeddings.
"""
from .models import Ticket


# ─────────────────────────────────────────────────────────
# Mapeamento de palavras-chave → sugestão por categoria
# Funciona como "base de conhecimento" padrão para cold start
# ─────────────────────────────────────────────────────────
KNOWLEDGE_BASE = [
    {
        "keywords": ["documento", "arquivo", "upload", "anexo", "pdf", "incluir", "enviar", "importar"],
        "suggestion": (
            "Olá! Para incluir documentos no sistema, siga os passos abaixo:\n\n"
            "1. Acesse o módulo correspondente e clique em 'Anexar Arquivo'.\n"
            "2. Os formatos aceitos são: PDF, DOCX, XLSX e imagens (JPG/PNG) com até 10 MB.\n"
            "3. Após o upload, confirme clicando em 'Salvar'.\n\n"
            "Caso o documento não apareça após o upload, tente limpar o cache do navegador (Ctrl+Shift+R) e repita o processo. "
            "Se o problema persistir, informe o nome do arquivo e o erro exibido para agilizarmos a análise."
        )
    },
    {
        "keywords": ["senha", "login", "acesso", "entrar", "bloqueado", "autenticar", "credencial"],
        "suggestion": (
            "Olá! Para problemas de acesso ao sistema:\n\n"
            "1. Verifique se está usando o CPF correto (somente números).\n"
            "2. Use a opção 'Esqueci minha senha' para redefinir via e-mail cadastrado.\n"
            "3. Após 5 tentativas incorretas, o acesso é bloqueado por 15 minutos.\n\n"
            "Se não tiver acesso ao e-mail cadastrado, entre em contato com o administrador da sua organização para reativação manual."
        )
    },
    {
        "keywords": ["lento", "devagar", "performance", "demora", "travando", "timeout", "carregando"],
        "suggestion": (
            "Olá! Para problemas de performance, recomendamos os seguintes passos:\n\n"
            "1. Verifique sua conexão com a internet (mínimo recomendado: 10 Mbps).\n"
            "2. Limpe o cache e cookies do navegador (Ctrl+Shift+Delete).\n"
            "3. Tente acessar em janela anônima para descartar extensões.\n"
            "4. Se o problema ocorrer em horários específicos, pode ser pico de uso — reinicie a página após alguns minutos.\n\n"
            "Informe o horário exato do ocorrido e seu navegador/versão para análise aprofundada."
        )
    },
    {
        "keywords": ["erro", "bug", "falha", "não funciona", "quebrando", "crash", "500", "exception"],
        "suggestion": (
            "Olá! Para analisar o erro relatado, precisamos de algumas informações:\n\n"
            "1. Qual a mensagem de erro exibida (um print seria ideal)?\n"
            "2. Em qual tela/funcionalidade o erro acontece?\n"
            "3. O erro é constante ou intermitente?\n"
            "4. Outro usuário da sua organização também consegue reproduzir?\n\n"
            "Com essas informações, consigo acionar a equipe técnica com prioridade para diagnóstico e correção."
        )
    },
    {
        "keywords": ["relatorio", "relatório", "exportar", "excel", "dado", "dashboard", "grafico", "gráfico"],
        "suggestion": (
            "Olá! Para exportar dados e relatórios:\n\n"
            "1. Acesse o Dashboard e use o filtro de período desejado.\n"
            "2. Clique em 'Exportar' no canto superior direito — disponível em XLSX e CSV.\n"
            "3. Para relatórios personalizados, use o módulo 'Relatórios Avançados'.\n\n"
            "Caso o arquivo exportado esteja vazio ou incompleto, verifique se há permissão de acesso ao período selecionado no perfil do seu usuário."
        )
    },
    {
        "keywords": ["usuario", "usuário", "cadastro", "criar conta", "novo colaborador", "permissao", "perfil"],
        "suggestion": (
            "Olá! Para gerenciar usuários e permissões:\n\n"
            "1. Somente ADMINs podem criar novos usuários — acesse 'Configurações > Usuários'.\n"
            "2. Defina o perfil: ADMIN, TÉCNICO ou CLIENTE.\n"
            "3. O novo usuário receberá um e-mail de boas-vindas com as instruções de acesso.\n\n"
            "Se precisar alterar permissões de um usuário existente, edite o perfil dele em 'Gerenciar Usuários' e salve as alterações."
        )
    },
    {
        "keywords": ["integração", "api", "webhook", "conectar", "sistema externo", "token"],
        "suggestion": (
            "Olá! Para integrações externas:\n\n"
            "1. Gere um token de API em 'Configurações > Integrações'.\n"
            "2. Use o endpoint base: https://api.syntivra.com/api/v1/\n"
            "3. Autentique todas as requisições com o header: Authorization: Bearer {seu_token}\n\n"
            "A documentação completa da API está disponível em /api/docs. "
            "Se precisar de um webhook específico para eventos do sistema, informe qual evento (criação de ticket, mudança de status, etc.) e a URL de destino."
        )
    },
]

GENERIC_FALLBACK = (
    "Olá! Recebemos seu chamado e nossa equipe técnica está analisando.\n\n"
    "Para agilizar a resolução:\n"
    "• Descreva com detalhes o que estava tentando fazer quando o problema ocorreu.\n"
    "• Se possível, inclua capturas de tela ou logs de erro.\n"
    "• Informe se o problema afeta outros usuários da sua organização.\n\n"
    "Nossa meta de atendimento é responder em até 4 horas para chamados de prioridade ALTA e 8 horas para os demais. "
    "Qualquer atualização será registrada aqui neste chamado. Obrigado!"
)


class AIService:

    @staticmethod
    def get_suggested_resolution(ticket):
        """
        Estratégia em 3 camadas:
        1. Similaridade textual com tickets resolvidos do mesmo tenant
        2. Knowledge base por categoria de keyword
        3. Fallback genérico profissional
        """
        # ── Camada 1: Busca por histórico do tenant ──────────────────
        suggestion = AIService._search_historical(ticket)
        if suggestion:
            return f"[Baseado em caso similar resolvido]\n\n{suggestion}"

        # ── Camada 2: Knowledge base por categoria ───────────────────
        suggestion = AIService._match_knowledge_base(ticket)
        if suggestion:
            return suggestion

        # ── Camada 3: Fallback genérico ──────────────────────────────
        return GENERIC_FALLBACK

    @staticmethod
    def _search_historical(ticket):
        """Busca por tickets resolvidos com texto similar no mesmo tenant."""
        resolved_qs = Ticket.objects.filter(
            organization=ticket.organization,
            status='RESOLVED'
        ).exclude(id=ticket.id)

        if not resolved_qs.exists():
            return ""

        # Extrai termos relevantes do título (ignora stop words e palavras curtas)
        stop_words = {'o', 'a', 'os', 'as', 'um', 'uma', 'de', 'da', 'do', 'em', 'no', 'na', 'com', 'para', 'por'}
        search_terms = [
            w for w in ticket.title.lower().split()
            if len(w) > 3 and w not in stop_words
        ]

        if not search_terms:
            return ""

        # Reduz progressivamente até encontrar match
        matches = resolved_qs
        for term in search_terms:
            candidate = matches.filter(title__icontains=term) | matches.filter(description__icontains=term)
            if candidate.exists():
                matches = candidate

        similar = matches.order_by('-created_at').first()
        if not similar:
            return ""

        last_msg = similar.messages.filter(is_ai_suggestion=False).order_by('-created_at').first()
        return last_msg.content if last_msg else ""

    @staticmethod
    def _match_knowledge_base(ticket):
        """Encontra a categoria mais relevante da knowledge base."""
        combined = f"{ticket.title} {ticket.description}".lower()
        best_match = None
        best_score = 0

        for entry in KNOWLEDGE_BASE:
            score = sum(1 for kw in entry["keywords"] if kw in combined)
            if score > best_score:
                best_score = score
                best_match = entry

        return best_match["suggestion"] if best_match and best_score > 0 else ""

    @staticmethod
    def get_sentiment(text):
        """
        Análise de sentimento por léxico weighted.
        Arquitetura preparada para integração com modelo NLP (BERT/transformers).
        """
        text = text.lower()

        angry_terms = {
            'urgente': 2, 'absurdo': 3, 'demora': 2, 'ruim': 2, 'erro': 1,
            'problema': 1, 'pior': 3, 'lixo': 3, 'raiva': 3, 'pessimo': 3,
            'horrivel': 3, 'inaceitavel': 3, 'ridiculo': 3, 'caindo': 2,
            'nao funciona': 2, 'quebrou': 2, 'travou': 2
        }
        positive_terms = {
            'obrigado': 2, 'agradeco': 2, 'otimo': 2, 'perfeito': 2,
            'valeu': 1, 'bom': 1, 'excelente': 2, 'resolvido': 2, 'funcionou': 2
        }

        angry_score = sum(weight for term, weight in angry_terms.items() if term in text)
        positive_score = sum(weight for term, weight in positive_terms.items() if term in text)

        if angry_score >= 2:
            return 'ANGRY'
        if positive_score >= 3:
            return 'POSITIVE'
        return 'NEUTRAL'
