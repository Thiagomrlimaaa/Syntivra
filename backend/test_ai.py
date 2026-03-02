import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, '.')
django.setup()

from apps.tickets.models import Ticket
from apps.tickets.ai_service import AIService

# Pega o ticket mais recente
ticket = Ticket.unfiltered_objects.order_by('-created_at').first()

if not ticket:
    print("Nenhum ticket encontrado no banco.")
else:
    print(f"Testando IA para ticket: '{ticket.title}'")
    print(f"  Org: {ticket.organization}")
    print(f"  Status: {ticket.status}")
    print()

    # Testa sentiment
    text = f"{ticket.title} {ticket.description}"
    sentiment = AIService.get_sentiment(text)
    print(f"Sentiment detectado: {sentiment}")
    print()

    # Testa sugestao
    suggestion = AIService.get_suggested_resolution(ticket)
    if suggestion:
        print("Sugestao gerada:")
        print("-" * 60)
        print(suggestion[:500])
        print("-" * 60)
    else:
        print("VAZIO - Nenhuma sugestao gerada!")

    # Testa geracao de mensagem manualmente
    from apps.tickets.models import TicketMessage
    existing_ai = TicketMessage.unfiltered_objects.filter(
        ticket=ticket, is_ai_suggestion=True
    )
    print(f"\nMensagens de IA existentes nesse ticket: {existing_ai.count()}")
    for m in existing_ai:
        print(f"  [{m.created_at}] {m.content[:100]}...")
