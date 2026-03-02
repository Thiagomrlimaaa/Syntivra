from django.contrib.auth import get_user_model
from django.db.models import Count
from .models import Ticket

User = get_user_model()

class TicketService:
    @staticmethod
    def assign_technician(ticket):
        """
        Estratégia: Menor Carga (Least Assigned)
        Atribui o ticket ao técnico da mesma organização que possui menos tickets abertos/em progresso.
        """
        from django.db.models import Q
        technicians = User.objects.filter(
            organization=ticket.organization,
            role__in=['TECHNICIAN', 'ADMIN'],
            is_active=True
        ).annotate(
            ticket_count=Count(
                'assigned_tickets', 
                filter=Q(assigned_tickets__status__in=['OPEN', 'PROGRESS'])
            )
        ).order_by('ticket_count')

        if technicians.exists():
            tech = technicians.first()
            # Deixar para o sinal ou atualizar sem salvar recursivamente
            ticket.assigned_to = tech
            # ticket.save() # Removido para evitar recursão infinita no post_save
            return tech
        return None
