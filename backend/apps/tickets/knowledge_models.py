"""
KnowledgeChunk — chunks indexados de documentos (PDFs, histórico, etc.)
AIConversationState — estado da conversa da IA por ticket
"""
from django.db import models
from apps.tenants.models import TenantModel
import uuid


class KnowledgeChunk(TenantModel):
    """
    Representa um trecho de conhecimento indexado.
    Pode vir de PDFs, histórico de tickets resolvidos, ou FAQs manuais.
    """
    class SourceType(models.TextChoices):
        PDF_MANUAL = 'PDF_MANUAL', 'Manual PDF'
        TICKET_HISTORY = 'TICKET_HISTORY', 'Histórico de Ticket'
        FAQ = 'FAQ', 'FAQ Manual'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    source_type = models.CharField(max_length=30, choices=SourceType.choices)
    source_name = models.CharField(max_length=255, help_text="Nome do arquivo PDF ou título do ticket de origem")
    
    # Conteúdo indexável
    keywords = models.TextField(help_text="Palavras-chave separadas por vírgula para busca rápida")
    question_hint = models.TextField(help_text="Termos/perguntas que este chunk responde")
    content = models.TextField(help_text="Resposta/conteúdo completo")
    
    # Metadados
    confidence_score = models.FloatField(default=1.0, help_text="0.0-1.0, confiança da resposta")
    page_reference = models.CharField(max_length=50, blank=True, help_text="Página do manual de referência")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-confidence_score', '-created_at']

    def __str__(self):
        return f"[{self.source_type}] {self.source_name}: {self.question_hint[:60]}"


class AIConversationState(TenantModel):
    """
    Rastreia o estado da conversa da IA para cada ticket.
    Permite que a IA faça perguntas sequenciais e mantenha contexto.
    """
    class State(models.TextChoices):
        GREETING = 'GREETING', 'Saudação inicial'
        ANALYZING = 'ANALYZING', 'Analisando o problema'
        ASKING = 'ASKING', 'Aguardando resposta do cliente'
        SUGGESTING = 'SUGGESTING', 'Sugestão aguardando aprovação do técnico'
        CONFIRMED = 'CONFIRMED', 'Resposta confirmada pelo técnico'
        NO_KNOWLEDGE = 'NO_KNOWLEDGE', 'Sem conhecimento — escalado'
        RESOLVED = 'RESOLVED', 'Resolvido'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ticket = models.OneToOneField(
        'tickets.Ticket',
        on_delete=models.CASCADE,
        related_name='ai_state'
    )
    state = models.CharField(max_length=20, choices=State.choices, default=State.GREETING)
    
    # Contexto acumulado da conversa
    pending_question = models.TextField(blank=True, help_text="Pergunta pendente feita pela IA")
    clarification_count = models.IntegerField(default=0, help_text="Quantas perguntas de clarificação já foram feitas")
    matched_chunk_id = models.UUIDField(null=True, blank=True, help_text="ID do KnowledgeChunk que melhor casou")
    confidence = models.FloatField(default=0.0, help_text="Confiança da última busca")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"AIState[{self.ticket.title[:30]}] → {self.state}"
