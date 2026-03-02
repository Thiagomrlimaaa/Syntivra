"""
Signals do app tickets — conecta eventos do Django às regras de negócio.
"""
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta

from .models import Ticket, TicketMessage
from .services import TicketService
from .ai_service import AIService  # mantem retrocompatibilidade
from .conversational_ai import ConversationalAIService
from .audit import AuditLog


@receiver(pre_save, sender=Ticket)
def handle_ticket_pre_save(sender, instance, **kwargs):
    """Executa antes de salvar o ticket: sentimento, SLA."""
    if not instance.id:
        # Novo ticket
        combined_text = f"{instance.title} {instance.description}"
        instance.sentiment = AIService.get_sentiment(combined_text)

        now = timezone.now()
        sla_mapping = {
            'CRITICAL': 2,
            'HIGH': 4,
            'MEDIUM': 8,
            'LOW': 24
        }
        hours = sla_mapping.get(instance.priority, 8)
        instance.sla_deadline = now + timedelta(hours=hours)


@receiver(post_save, sender=Ticket)
def handle_ticket_post_save(sender, instance, created, **kwargs):
    """Executa após salvar o ticket."""
    if created:
        # 1. Atribuição automática de técnico (round-robin / menor carga)
        if not instance.assigned_to:
            tech = TicketService.assign_technician(instance)
            if tech:
                Ticket.objects.filter(id=instance.id).update(assigned_to=tech)

        # 2. Log de auditoria
        AuditLog.objects.create(
            organization=instance.organization,
            actor=instance.created_by,
            action="CREATED",
            target_model="Ticket",
            target_id=str(instance.id)
        )

        # 3. IA Conversacional — inicia a conversa
        try:
            ai_response = ConversationalAIService.start_conversation(instance)
            if ai_response and ai_response.strip():
                TicketMessage.objects.create(
                    organization=instance.organization,
                    ticket=instance,
                    author=None,           # IA não tem author humano
                    content=ai_response,
                    is_ai_suggestion=True
                )
                Ticket.objects.filter(id=instance.id).update(status='PENDING_TECH')
        except Exception as e:
            print(f"[AI] Erro ao iniciar conversa para ticket {instance.id}: {e}")

    else:
        # Update: verifica se o ticket foi resolvido para aprender
        if instance.status == 'RESOLVED':
            try:
                ConversationalAIService.learn_from_resolution(instance)
            except Exception as e:
                print(f"[AI] Erro ao aprender com resolução do ticket {instance.id}: {e}")


@receiver(post_save, sender=TicketMessage)
def handle_message_post_save(sender, instance, created, **kwargs):
    """
    Ao receber uma nova mensagem humana do cliente, verifica se a IA
    deve responder (continuar a conversa ou pedir mais detalhes).
    """
    if not created:
        return

    # Só processa mensagens humanas (não as da própria IA)
    if instance.is_ai_suggestion or instance.author is None:
        return

    ticket = instance.ticket

    # IA só responde se o ticket ainda está aberto
    if ticket.status in ['RESOLVED', 'CANCELLED']:
        return

    # Verifica se quem enviou é o CLIENTE (IA responde ao cliente, não ao técnico)
    if hasattr(instance.author, 'role') and instance.author.role != 'CUSTOMER':
        return

    try:
        ai_response = ConversationalAIService.process_reply(ticket, instance.content)
        if ai_response and ai_response.strip():
            TicketMessage.objects.create(
                organization=ticket.organization,
                ticket=ticket,
                author=None,
                content=ai_response,
                is_ai_suggestion=True
            )
    except Exception as e:
        print(f"[AI] Erro ao processar resposta para ticket {ticket.id}: {e}")
