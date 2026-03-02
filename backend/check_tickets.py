import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, '.')
django.setup()

from apps.tickets.models import Ticket, TicketMessage

print("=== Tickets no banco (unfiltered) ===")
for t in Ticket.unfiltered_objects.all().order_by('-created_at'):
    msgs = TicketMessage.unfiltered_objects.filter(ticket=t)
    ai_msgs = msgs.filter(is_ai_suggestion=True)
    print(f"  [{str(t.id)[:8]}] '{t.title}' | status={t.status} | org={t.organization} | msgs={msgs.count()} | ai_msgs={ai_msgs.count()}")
    for m in ai_msgs:
        print(f"    [AI] {m.content[:80]}...")
    for m in msgs.filter(is_ai_suggestion=False):
        print(f"    [Human] {m.content[:80]}")
