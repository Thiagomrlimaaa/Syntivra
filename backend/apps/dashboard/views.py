from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from django.db.models import Count, Avg, F
from django.utils import timezone
from apps.tickets.models import Ticket
from apps.users.permissions import IsAdminUser, IsTechnicianUser

class DashboardMetricsView(APIView):
    # ADMIN e TECHNICIAN têm acesso ao dashboard
    permission_classes = [permissions.IsAuthenticated, IsTechnicianUser]

    def get(self, request):
        organization = request.user.organization

        # Garante isolamento multi-tenant — filtra sempre pela organização do usuário logado
        base_qs = Ticket.objects.filter(organization=organization)

        # 1. Contagem por Status
        tickets_by_status = list(
            base_qs.values('status').annotate(total=Count('id'))
        )

        # 2. Contagem por Prioridade
        tickets_by_priority = list(
            base_qs.values('priority').annotate(total=Count('id'))
        )

        # 3. Tempo Médio de Resolução (MTTR) em horas
        resolved_qs = base_qs.filter(status='RESOLVED')
        mttr = resolved_qs.annotate(
            duration=F('updated_at') - F('created_at')
        ).aggregate(avg_duration=Avg('duration'))['avg_duration']

        mttr_hours = mttr.total_seconds() / 3600 if mttr else 0

        # 4. Total de tickets abertos
        open_count = base_qs.filter(status='OPEN').count()

        # 5. Produtividade por Técnico (tickets resolvidos por técnico)
        technician_productivity = list(
            resolved_qs.values(
                'assigned_to__first_name', 'assigned_to__last_name'
            ).annotate(resolved_count=Count('id')).order_by('-resolved_count')
        )

        # 6. IA Analytics
        ai_assisted_count = base_qs.filter(ai_assisted=True).count()
        ai_knowledge_gaps = base_qs.filter(ai_knowledge_gap=True).count()
        total_tickets = base_qs.count()
        ai_efficiency = round((ai_assisted_count / (total_tickets or 1)) * 100, 1)

        return Response({
            "tickets_by_status": tickets_by_status,
            "tickets_by_priority": tickets_by_priority,
            "mttr_hours": round(mttr_hours, 2),
            "open_count": open_count,
            "technician_productivity": technician_productivity,
            "ai_stats": {
                "assisted": ai_assisted_count,
                "gaps": ai_knowledge_gaps,
                "efficiency_pct": ai_efficiency
            }
        })
