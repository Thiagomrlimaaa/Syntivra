import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, '.')
django.setup()

from apps.tickets.models import Ticket, TicketMessage
from apps.tickets.ai_service import AIService

# Pega todos os tickets OPEN/IN_PROGRESS sem sugestao de IA
tickets_sem_sugestao = Ticket.unfiltered_objects.exclude(
    messages__is_ai_suggestion=True
).filter(status__in=['OPEN', 'PROGRESS', 'HOLD'])

print(f"Tickets sem sugestao de IA: {tickets_sem_sugestao.count()}")

for ticket in tickets_sem_sugestao:
    suggestion = AIService.get_suggested_resolution(ticket)
    if suggestion:
        msg = TicketMessage.unfiltered_objects.create(
            organization=ticket.organization,
            ticket=ticket,
            author=None,
            content=suggestion,
            is_ai_suggestion=True
        )
        print(f"  Sugestao injetada no ticket '{ticket.title}' (id={str(ticket.id)[:8]})")
    else:
        print(f"  Sem sugestao para ticket '{ticket.title}'")

print("\nConcluido.")
