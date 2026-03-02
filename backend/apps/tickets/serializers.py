from rest_framework import serializers
from .models import Ticket, TicketMessage
from apps.users.serializers import UserSerializer

class TicketSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    assigned_to = UserSerializer(read_only=True)
    organization = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Ticket
        fields = [
            'id', 'title', 'description', 'status', 'priority', 'sentiment', 'sla_deadline',
            'created_by', 'assigned_to', 'organization', 
            'ai_performance_score', 'ai_knowledge_gap', 'ai_assisted',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by', 'organization', 'sentiment', 'sla_deadline', 'created_at', 'updated_at', 'ai_performance_score', 'ai_knowledge_gap', 'ai_assisted']

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['created_by'] = user
        validated_data['organization'] = user.organization
        return super().create(validated_data)

class TicketUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ['status', 'priority', 'assigned_to', 'description']

class TicketMessageSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    
    class Meta:
        model = TicketMessage
        fields = ['id', 'author', 'content', 'file_attachment', 'is_ai_suggestion', 'created_at']
        read_only_fields = ['author', 'is_ai_suggestion', 'created_at']
