from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Ticket, TicketMessage, KnowledgeChunk
from .serializers import TicketSerializer, TicketUpdateSerializer, TicketMessageSerializer
from apps.users.permissions import IsTechnicianUser
from .conversational_ai import ConversationalAIService
from .knowledge_models import AIConversationState


class TicketViewSet(viewsets.ModelViewSet):

    def get_queryset(self):
        user = self.request.user
        if user.role == 'CUSTOMER':
            # Clientes só veem tickets que eles criaram
            return Ticket.objects.filter(created_by=user).order_by('-created_at')
        # ADMIN e TECHNICIAN veem todos os tickets da organização (multi-tenant via TenantManager)
        return Ticket.objects.all().order_by('-created_at')

    def get_serializer_class(self):
        return TicketSerializer

    def get_permissions(self):
        if self.action in ['destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user,
            organization=self.request.user.organization
        )

    @action(detail=True, methods=['get', 'post'], permission_classes=[permissions.IsAuthenticated])
    def messages(self, request, pk=None):
        ticket = self.get_object()

        if request.method == 'GET':
            # Usa unfiltered_objects + filtro explícito por ticket para garantir
            # que a busca não seja bloqueada pelo TenantManager durante o timing JWT.
            # O isolamento é garantido pelo próprio ticket (que pertence ao tenant correto).
            messages = TicketMessage.unfiltered_objects.filter(
                ticket=ticket
            ).order_by('created_at')
            
            # Se for cliente (servidor), não enxerga sugestões internas da IA
            if request.user.role == 'CUSTOMER':
                messages = messages.filter(is_ai_suggestion=False)

            serializer = TicketMessageSerializer(messages, many=True)
            return Response(serializer.data)

        elif request.method == 'POST':
            serializer = TicketMessageSerializer(data=request.data)
            if serializer.is_valid():
                msg = serializer.save(
                    ticket=ticket,
                    author=request.user,
                    organization=ticket.organization
                )
                
                # Se for técnico, e o ticket tinha uma sugestão de IA pendente, 
                # consideramos que esta resposta (mesmo que editada) resolve o caso.
                if request.user.role == 'TECHNICIAN':
                    ConversationalAIService.learn_from_resolution(ticket)
                
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], permission_classes=[IsTechnicianUser])
    def knowledge_gaps(self, request):
        """Lista chamados onde a IA não soube responder (para treinamento)."""
        gaps = Ticket.objects.filter(ai_knowledge_gap=True).order_by('-created_at')
        serializer = TicketSerializer(gaps, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsTechnicianUser])
    def train_ai(self, request, pk=None):
        """Transforma a solução de um ticket em conhecimento oficial para a IA."""
        ticket = self.get_object()
        solution = request.data.get('solution')
        
        if not solution:
            return Response({"error": "Solução é obrigatória"}, status=status.HTTP_400_BAD_REQUEST)
            
        # Cria o KnowledgeChunk
        KnowledgeChunk.objects.create(
            source_type=KnowledgeChunk.SourceType.FAQ,
            source_name=f"Treinamento Ticket #{ticket.id}",
            keywords=ticket.title,
            question_hint=ticket.description[:200],
            content=solution,
            confidence_score=1.0,
            organization=ticket.organization
        )
        
        # Marca como resolvido o gap
        ticket.ai_knowledge_gap = False
        ticket.save()
        
        return Response({"status": "IA Treinada com sucesso!"})

    @action(detail=True, methods=['post'], url_path=r'messages/(?P<msg_id>\d+)/reject', permission_classes=[IsTechnicianUser])
    def reject_ai_suggestion(self, request, pk=None, msg_id=None):
        """Técnico rejeitou a sugestão da IA. Marca como GAP de conhecimento."""
        ticket = self.get_object()
        
        # Penaliza a performance da IA
        ticket.ai_performance_score = -1
        ticket.ai_knowledge_gap = True
        ticket.save()

        # Atualiza o estado da IA para NO_KNOWLEDGE (já que falhou)
        try:
            state = AIConversationState.objects.get(ticket=ticket)
            state.state = AIConversationState.State.NO_KNOWLEDGE
            state.save()
        except AIConversationState.DoesNotExist:
            pass

        # Remove a mensagem de sugestão
        TicketMessage.objects.filter(id=msg_id, ticket=ticket, is_ai_suggestion=True).delete()
        
        return Response({"status": "Sugestão rejeitada e enviada para o Centro de Treinamento."})

    @action(detail=True, methods=['delete'], url_path=r'messages/(?P<msg_id>\d+)', permission_classes=[permissions.IsAuthenticated])
    def delete_message(self, request, pk=None, msg_id=None):
        ticket = self.get_object()
        TicketMessage.objects.filter(id=msg_id, ticket=ticket).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
