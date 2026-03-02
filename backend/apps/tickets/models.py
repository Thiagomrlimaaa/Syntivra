from django.db import models
from django.conf import settings
from apps.tenants.models import TenantModel
from .knowledge_models import KnowledgeChunk, AIConversationState

__all__ = ['Ticket', 'TicketMessage', 'KnowledgeChunk', 'AIConversationState']

class Ticket(TenantModel):
    class Status(models.TextChoices):
        OPEN = 'OPEN', 'Aberto'
        PENDING_TECH = 'PENDING_TECH', 'Aguardando Validação'
        WAITING_USER = 'WAITING_USER', 'Aguardando Confirmação'
        IN_PROGRESS = 'PROGRESS', 'Em Andamento'
        HOLD = 'HOLD', 'Em Espera'
        REOPENED = 'REOPENED', 'Reaberto'
        RESOLVED = 'RESOLVED', 'Concluído'
        CANCELLED = 'CANCELLED', 'Cancelado'

    class Priority(models.TextChoices):
        LOW = 'LOW', 'Baixa'
        MEDIUM = 'MEDIUM', 'Média'
        HIGH = 'HIGH', 'Alta'
        CRITICAL = 'CRITICAL', 'Crítica'

    class Sentiment(models.TextChoices):
        ANGRY = 'ANGRY', 'Irritado'
        NEUTRAL = 'NEUTRAL', 'Neutro'
        POSITIVE = 'POSITIVE', 'Satisfeito'

    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(
        max_length=20, 
        choices=Status.choices, 
        default=Status.OPEN
    )
    priority = models.CharField(
        max_length=20, 
        choices=Priority.choices, 
        default=Priority.MEDIUM
    )
    sentiment = models.CharField(
        max_length=20,
        choices=Sentiment.choices,
        default=Sentiment.NEUTRAL
    )
    sla_deadline = models.DateTimeField(null=True, blank=True)
    
    # AI Performance Tracking
    ai_performance_score = models.IntegerField(default=0, help_text="-1: Rejeitado, 0: Neutro, 1: Validado")
    ai_knowledge_gap = models.BooleanField(default=False, help_text="True se a IA não soube responder")
    ai_assisted = models.BooleanField(default=False, help_text="True se teve ajuda da IA")
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_tickets'
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tickets'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"#{self.id} - {self.title}"

class TicketMessage(TenantModel):
    ticket = models.ForeignKey(
        Ticket, 
        on_delete=models.CASCADE, 
        related_name='messages'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='messages'
    )
    content = models.TextField()
    file_attachment = models.FileField(upload_to='attachments/%Y/%m/%d/', null=True, blank=True)
    is_ai_suggestion = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message by {self.author} on Ticket #{self.ticket.id}"

