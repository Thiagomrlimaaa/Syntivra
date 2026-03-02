"""
ConversationalAIService — Motor de IA Conversacional do Syntivra OS
====================================================================
Sistema baseado em E-Palmas / SIGED (IKHON Tecnologia)
Comportamento:
  1. Saúda o cliente com naturalidade (Bom dia/Boa tarde/Boa noite)
  2. Analisa o assunto e detalhes do chamado
  3. Se tiver conhecimento → gera resposta completa para aprovação do técnico
  4. Se tiver dúvida → faz perguntas de clarificação (máx. 2)
  5. Se não tiver conhecimento → informa honestamente e escala para técnico
  6. Aprende com as respostas dos técnicos (histórico de tickets resolvidos)
"""
import re
import random
from datetime import datetime
from .knowledge_models import KnowledgeChunk, AIConversationState


# ─────────────────────────────────────────────────────────────────────────────
# MENSAGENS DIRETAS (Padrão IA Suporte)
# ─────────────────────────────────────────────────────────────────────────────

QUESTION_PHRASES = [
    "Preciso de uma informação adicional:",
    "Para continuar, me responda:",
]

NO_KNOWLEDGE_PHRASES = [
    "Ainda não tenho uma resposta confirmada para esse caso específico na minha base de conhecimento.",
    "Para garantir a precisão do seu atendimento, não vou sugerir uma resposta automática agora.",
]

ESCALATION_SUFFIX = (
    "\n\nJá notifiquei nossa equipe técnica sobre a sua dúvida. Um especialista analisará o seu chamado e entrará em contato em breve para te auxiliar! 😊"
)


# ─────────────────────────────────────────────────────────────────────────────
# PERGUNTAS DE CLARIFICAÇÃO POR CATEGORIA
# ─────────────────────────────────────────────────────────────────────────────

CLARIFICATION_QUESTIONS = {
    "documento": [
        "Você está tentando incluir um arquivo digital a um documento já cadastrado, ou quer cadastrar um documento novo do zero?",
        "O arquivo que você quer incluir está em formato PDF? O sistema E-Palmas aceita apenas arquivos em formato PDF para upload.",
        "Qual é o número do protocolo (NUP) do documento em que deseja incluir o arquivo?",
    ],
    "processo": [
        "Você quer criar um processo novo ou está tentando movimentar (tramitar) um processo que já existe?",
        "O processo está na carga do seu departamento ou foi tramitado para outro setor?",
        "Qual é o NUP (número de protocolo) do processo que está com problema?",
    ],
    "tramitar": [
        "Para qual departamento ou secretaria você está tentando tramitar o documento?",
        "O documento já foi recebido pelo departamento de destino? Se sim, a tramitação não pode ser cancelada.",
        "O documento está no status 'Corrente' na sua listagem?",
    ],
    "arquivar": [
        "Você quer arquivar o documento fisicamente (com localização de caixa) ou apenas arquivar virtualmente no sistema?",
        "O documento está na carga do seu departamento? Só é possível arquivar documentos em carga.",
    ],
    "assinatura": [
        "Você vai assinar através de Certificado Digital (token/smart card) ou através de Login e Senha?",
        "O arquivo digital já foi inserido no documento? A assinatura só pode ser feita em arquivos já anexados.",
    ],
    "cancelar": [
        "Você quer cancelar a tramitação (voltar o documento ao remetente) ou cancelar o próprio documento (retirar validade)?",
        "A tramitação já foi recebida pelo departamento de destino? Se sim, não é possível cancelar — o documento precisa ser tramitado de volta.",
    ],
    "pesquisa": [
        "Você sabe o número do protocolo (NUP) do documento? Se sim, use a Pesquisa Simples. Se não, use a Pesquisa Avançada.",
        "Quais informações você tem sobre o documento? (NUP, data, tipo documental, interessado, assunto?)",
    ],
    "acesso": [
        "O erro aparece ao tentar acessar o sistema (login) ou dentro de alguma funcionalidade específica?",
        "Qual é o perfil do seu usuário no sistema? (Administrador, Técnico, Protocolo, etc.)",
    ],
    "default": [
        "Poderia me descrever com mais detalhes o que aconteceu? Em qual tela ou funcionalidade do sistema o problema ocorreu?",
        "O problema acontece sempre ou em situações específicas? (ex: com um documento em particular, só em um computador, etc.)",
    ],
}


def _get_clarification_questions(category: str, already_asked: int) -> str:
    questions = CLARIFICATION_QUESTIONS.get(category, CLARIFICATION_QUESTIONS["default"])
    if already_asked < len(questions):
        return questions[already_asked]
    return CLARIFICATION_QUESTIONS["default"][0]


# ─────────────────────────────────────────────────────────────────────────────
# MOTOR DE BUSCA NA BASE DE CONHECIMENTO
# ─────────────────────────────────────────────────────────────────────────────

def _normalize(text: str) -> str:
    """Normaliza texto para comparação: lowercase, remove acentos comuns."""
    text = text.lower()
    replacements = {
        'ã': 'a', 'â': 'a', 'á': 'a', 'à': 'a',
        'ê': 'e', 'é': 'e', 'è': 'e',
        'î': 'i', 'í': 'i',
        'ô': 'o', 'ó': 'o', 'õ': 'o',
        'ú': 'u', 'û': 'u', 'ü': 'u',
        'ç': 'c',
    }
    for accented, plain in replacements.items():
        text = text.replace(accented, plain)
    return text


def _detect_category(text: str) -> tuple[str, float]:
    """
    Detecta a categoria do chamado baseada em palavras-chave.
    Retorna (categoria, score de confiança 0-1).
    """
    normalized = _normalize(text)

    category_keywords = {
        "documento": [
            "documento", "incluir", "arquivo", "pdf", "anexar", "upload",
            "digital", "cadastrar documento", "nup", "protocolo", "arquivo digital",
        ],
        "processo": [
            "processo", "formalizar", "autuacao", "autuação", "processo geral",
            "fluxo", "workflow", "modulo processo", "módulo processo",
        ],
        "tramitar": [
            "tramitar", "tramitacao", "tramitação", "encaminhar", "enviar",
            "expedir", "distribuir", "receber", "movimentar",
        ],
        "arquivar": [
            "arquivar", "arquivamento", "caixa", "guarda", "desarquivar",
            "arquivo corrente", "passivo",
        ],
        "assinatura": [
            "assinar", "assinatura", "certificado digital", "token",
            "assinatura digital", "autenticar",
        ],
        "cancelar": [
            "cancelar", "cancelamento", "reativar", "reativacao",
            "cancelar tramitacao", "cancelar documento",
        ],
        "pesquisa": [
            "pesquisar", "pesquisa", "buscar", "encontrar", "localizar",
            "pesquisa avancada", "pesquisa simples",
        ],
        "acesso": [
            "acesso", "login", "senha", "entrar", "permissao", "perfil",
            "bloqueado", "usuario", "credencial",
        ],
    }

    scores = {}
    for category, keywords in category_keywords.items():
        score = sum(1 for kw in keywords if kw in normalized)
        if score > 0:
            scores[category] = score

    if not scores:
        return "default", 0.0

    # Cálculo de confiança baseado na densidade de palavras-chave
    final_scores = {}
    for cat, score in scores.items():
        # Penaliza categorias com muitas keywords onde poucas bateram
        density = score / len(category_keywords[cat])
        final_scores[cat] = score * (1 + density)

    best = max(final_scores, key=final_scores.get)
    
    # Confiança precisa ser alta para cravar uma categoria
    raw_score = scores[best]
    confidence = min(raw_score / 2.0, 1.0) # Precisa de pelo menos 2 keywords para 100%
    
    return best, confidence


def _search_knowledge_base(text: str, category: str) -> tuple[KnowledgeChunk | None, float]:
    """Busca no banco de KnowledgeChunks."""
    normalized = _normalize(text)
    words = [w for w in normalized.split() if len(w) > 3]

    if not words:
        return None, 0.0

    chunks = KnowledgeChunk.objects.filter(is_active=True)

    # FILTRO CRÍTICO: Se a categoria detectada for forte, limita a busca a ela
    # Isso impede que palavras como 'documento' em um contexto de 'arquivar' puxem
    # manuais de 'como anexar documento'.
    category_chunks = chunks.filter(keywords__icontains=category)
    if category_chunks.exists():
        chunks = category_chunks
    elif category != "default":
        # Se detectou algo mas não tem no KB, a chance de erro é alta ao buscar em tudo
        return None, 0.0

    best_chunk = None
    best_score = 0

    for chunk in chunks:
        chunk_normalized = _normalize(f"{chunk.keywords} {chunk.question_hint} {chunk.content}")
        score = sum(1 for w in words if w in chunk_normalized)
        weighted_score = score * chunk.confidence_score

        if weighted_score > best_score:
            best_score = weighted_score
            best_chunk = chunk

    normalized_score = min(best_score / max(len(words) * 0.4, 1), 1.0)
    return best_chunk, normalized_score


def _search_ticket_history(ticket) -> tuple[str, float]:
    """Busca em tickets resolvidos similares do mesmo tenant."""
    from .models import Ticket as TicketModel

    resolved = TicketModel.unfiltered_objects.filter(
        organization=ticket.organization,
        status='RESOLVED'
    ).exclude(id=ticket.id)

    if not resolved.exists():
        return "", 0.0

    stop_words = {'o', 'a', 'os', 'as', 'um', 'uma', 'de', 'da', 'do', 'em',
                  'no', 'na', 'com', 'para', 'por', 'que', 'e', 'ou', 'se'}
    terms = [w for w in _normalize(ticket.title + ' ' + ticket.description).split()
             if len(w) > 3 and w not in stop_words]

    best_ticket = None
    best_score = 0

    for t in resolved:
        t_text = _normalize(f"{t.title} {t.description}")
        score = sum(1 for term in terms if term in t_text)
        if score > best_score:
            best_score = score
            best_ticket = t

def _get_ticket_solution_text(ticket) -> str:
    """Acumula todas as 'Respostas Oficiais' de um ticket ou pega a melhor mensagem."""
    human_msgs = ticket.messages.filter(
        is_ai_suggestion=False,
        author__isnull=False
    ).order_by('created_at')

    official_texts = []
    fallback_text = ""

    for msg in human_msgs:
        content = msg.content.strip()
        if "Resposta Oficial:" in content:
            parts = content.split("Resposta Oficial:")
            if len(parts) > 1:
                clean_part = parts[1].strip()
                # Impede frases soltas muito genéricas ou curtas (menos de 3 palavras)
                if len(clean_part.split()) >= 3:
                    official_texts.append(clean_part)
        else:
            # Guarda as últimas mensagens substanciais se não tiver o selo Oficial
            if len(content) > 30 and len(content.split()) >= 5:
                fallback_text = content

    if official_texts:
        # Quando houver múltiplas respostas oficiais, considera todas juntas
        return "\n\n".join(official_texts)

    return fallback_text


def _search_ticket_history(ticket) -> tuple[str, float]:
    """Busca em tickets resolvidos similares do mesmo tenant."""
    from .models import Ticket as TicketModel

    resolved = TicketModel.unfiltered_objects.filter(
        organization=ticket.organization,
        status='RESOLVED'
    ).exclude(id=ticket.id)

    if not resolved.exists():
        return "", 0.0

    stop_words = {'o', 'a', 'os', 'as', 'um', 'uma', 'de', 'da', 'do', 'em',
                  'no', 'na', 'com', 'para', 'por', 'que', 'e', 'ou', 'se'}
    terms = [w for w in _normalize(ticket.title + ' ' + ticket.description).split()
             if len(w) > 3 and w not in stop_words]

    best_ticket = None
    best_score = 0

    for t in resolved:
        t_text = _normalize(f"{t.title} {t.description}")
        score = sum(1 for term in terms if term in t_text)
        if score > best_score:
            best_score = score
            best_ticket = t

    if not best_ticket or best_score == 0:
        return "", 0.0

    solution = _get_ticket_solution_text(best_ticket)
    if not solution:
        return "", 0.0

    confidence = min(best_score / max(len(terms) * 0.5, 1), 0.85)
    return solution, confidence


# ─────────────────────────────────────────────────────────────────────────────
# SERVIÇO PRINCIPAL
# ─────────────────────────────────────────────────────────────────────────────

class ConversationalAIService:

    @staticmethod
    def start_conversation(ticket) -> str:
        """
        Inicia a conversa ao criar o ticket.
        Gera a primeira mensagem da IA: saudação + análise + resposta ou pergunta.
        """
        combined_text = f"{ticket.title} {ticket.description}"
        category, cat_confidence = _detect_category(combined_text)

        # Cria o estado de conversa
        state_obj, _ = AIConversationState.objects.get_or_create(
            ticket=ticket,
            defaults={
                'state': AIConversationState.State.GREETING,
                'organization': ticket.organization
            }
        )

        # Tenta buscar conhecimento imediatamente
        chunk, chunk_score = _search_knowledge_base(combined_text, category)
        hist_content, hist_score = _search_ticket_history(ticket)

        # Caso A: Conhecimento sólido no KB ou histórico → resposta completa para aprovação
        # A regra de negócios exige que se o histórico humano resolver (sucesso passado), ele
        # seja a prioridade mestre e sem frases genéricas.
        # Aumetamos o threshold para 0.70 para evitar respostas irrelevantes
        best_score = max(chunk_score, hist_score)

        if best_score >= 0.70:
            # Se o Histórico (resposta do técnico) ganhou ou empatou, envia a resposta pura do humano
            if hist_score >= chunk_score and hist_content:
                state_obj.state = AIConversationState.State.SUGGESTING
                state_obj.confidence = hist_score
                state_obj.save()

                return hist_content
            
            # Se o PDF manual original ganhou, envia a formatação seca do manual
            elif chunk:
                content = chunk.content
                state_obj.state = AIConversationState.State.SUGGESTING
                state_obj.matched_chunk_id = chunk.id
                state_obj.confidence = chunk_score
                state_obj.save()

                return content

        # Caso B: Confiança média → faz pergunta de clarificação
        elif cat_confidence >= 0.1 or best_score >= 0.2:
            question = _get_clarification_questions(category, 0)
            state_obj.state = AIConversationState.State.ASKING
            state_obj.pending_question = question
            state_obj.clarification_count = 1
            state_obj.save()

            phrase = random.choice(QUESTION_PHRASES)
            return f"{phrase}\n\n{question}"

        # Caso C: Sem conhecimento → escala honestamente
        else:
            state_obj.state = AIConversationState.State.NO_KNOWLEDGE
            state_obj.save()
            
            # Marca o ticket como 'Gap de Conhecimento' para treinamento posterior
            ticket.ai_knowledge_gap = True
            ticket.save()

            no_knowledge = random.choice(NO_KNOWLEDGE_PHRASES)
            return f"{no_knowledge}{ESCALATION_SUFFIX}"

    @staticmethod
    def process_reply(ticket, new_message_content: str) -> str | None:
        """
        Processa uma nova mensagem do cliente e decide a próxima ação da IA.
        Retorna a resposta da IA ou None se não deve responder.
        """
        try:
            state_obj = AIConversationState.objects.get(ticket=ticket)
        except AIConversationState.DoesNotExist:
            return None

        # IA não responde se já confirmou ou escalonou
        if state_obj.state in [
            AIConversationState.State.CONFIRMED,
            AIConversationState.State.RESOLVED,
            AIConversationState.State.NO_KNOWLEDGE,
        ]:
            return None

        # IA está aguardando clarificação → reagir à resposta do cliente
        if state_obj.state == AIConversationState.State.ASKING:
            combined_text = f"{ticket.title} {ticket.description} {new_message_content}"
            category, cat_confidence = _detect_category(combined_text)

            chunk, chunk_score = _search_knowledge_base(combined_text, category)
            hist_content, hist_score = _search_ticket_history(ticket)
            best_score = max(chunk_score, hist_score)

            # Threshold de 0.70 para precisão máxima na resposta sugerida
            if best_score >= 0.70:
                # Agora tem resposta
                # Se o Histórico (resposta do técnico) ganhou ou empatou, envia a resposta pura
                if hist_score >= chunk_score and hist_content:
                    state_obj.state = AIConversationState.State.SUGGESTING
                    state_obj.confidence = hist_score
                    state_obj.save()

                    return hist_content
                # Senão, usa o KB (manual)
                elif chunk:
                    content = chunk.content
                    state_obj.state = AIConversationState.State.SUGGESTING
                    state_obj.matched_chunk_id = chunk.id
                    state_obj.confidence = chunk_score
                    state_obj.save()

                    return content

            elif state_obj.clarification_count < 2:
                # Faz mais uma pergunta de clarificação
                question = _get_clarification_questions(category, state_obj.clarification_count)
                state_obj.pending_question = question
                state_obj.clarification_count += 1
                state_obj.save()

                phrase = random.choice(QUESTION_PHRASES)
                return f"{phrase}\n\n{question}"

            else:
                # Esgotou perguntas ou confiança muito baixa → escala
                state_obj.state = AIConversationState.State.NO_KNOWLEDGE
                state_obj.save()

                return (
                    f"Entendi perfeitamente sua dúvida, mas prefiro que um de nossos técnicos valide a melhor forma de proceder neste caso.\n\n"
                    f"Eles já receberam um alerta sobre o seu chamado e logo você terá um retorno definitivo! 😊"
                )

        return None

    @staticmethod
    def confirm_suggestion(ticket, score=1) -> None:
        """Marca a sugestão como confirmada pelo técnico."""
        try:
            state_obj = AIConversationState.objects.get(ticket=ticket)
            state_obj.state = AIConversationState.State.CONFIRMED
            state_obj.save()
            
            # Tracking de performance
            ticket.ai_assisted = True
            ticket.ai_performance_score = score # Sucesso (1)
            ticket.save()
        except AIConversationState.DoesNotExist:
            pass

    @staticmethod
    def learn_from_resolution(ticket) -> None:
        """
        Ao resolver um ticket, cria/atualiza um KnowledgeChunk
        com o par pergunta→resposta aprendido dos técnicos.
        """
        content_to_learn = _get_ticket_solution_text(ticket)
        
        if not content_to_learn or len(content_to_learn) < 20:
            return  # Mensagem muito curta para aprender ou não tem contexto

        category, _ = _detect_category(f"{ticket.title} {ticket.description}")

        # Extrai keywords do título (para busca futura)
        stop_words = {'o', 'a', 'os', 'as', 'um', 'uma', 'de', 'da', 'do', 'em',
                      'no', 'na', 'com', 'para', 'por', 'que', 'e', 'ou', 'se'}
        keywords = [w for w in _normalize(ticket.title).split()
                    if len(w) > 3 and w not in stop_words]

        # Usa update_or_create para garantir que só aprendemos o "conhecimento final" deste ticket
        # e não tenhamos duplicatas se o técnico mandar várias mensagens.
        KnowledgeChunk.objects.update_or_create(
            source_name=f"Ticket #{str(ticket.id)[:8]} - {ticket.title[:50]}",
            organization=ticket.organization,
            defaults={
                'source_type': KnowledgeChunk.SourceType.TICKET_HISTORY,
                'keywords': f"{category}, {', '.join(keywords[:10])}",
                'question_hint': f"{ticket.title}: {ticket.description[:200]}",
                'content': content_to_learn,
                'confidence_score': 0.99,
                'page_reference': ""
            }
        )
