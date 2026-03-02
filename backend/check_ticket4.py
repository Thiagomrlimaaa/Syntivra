import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, '.')
django.setup()

from apps.tickets.models import Ticket, TicketMessage

# Verifica o ticket 4 em detalhes
t = Ticket.unfiltered_objects.get(title__iexact='incluir documento', status='OPEN')
print(f"Ticket: [{str(t.id)[:8]}] '{t.title}' | org={t.organization}")
print()

msgs = TicketMessage.unfiltered_objects.filter(ticket=t).order_by('created_at')
print(f"Total de mensagens: {msgs.count()}")
print()
for m in msgs:
    print(f"  id={str(m.id)[:8]} | is_ai={m.is_ai_suggestion} | author={m.author} | org={m.organization}")
    print(f"  content={m.content[:120]!r}")
    print()
