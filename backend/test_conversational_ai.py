import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, '.')
django.setup()

from apps.tickets.knowledge_models import KnowledgeChunk
from apps.tickets.conversational_ai import ConversationalAIService, _detect_category, _search_knowledge_base

print("=== Teste do Sistema Conversacional de IA ===\n")

# Teste 1: Deteccao de categoria
test_texts = [
    "Incluir Documento no sistema",
    "Como fazer upload de arquivo PDF",
    "Nao consigo tramitar meu processo",
    "Quero arquivar meu documento",
    "Como funciona a assinatura digital",
    "Sistema lento nao carrega",
    "Quero saber o que e o NUP",
    "Nao tenho permissao para acessar nada",
]

print("--- Deteccao de categorias ---")
for text in test_texts:
    cat, conf = _detect_category(text)
    chunk, score = _search_knowledge_base(text, cat)
    chunk_name = chunk.question_hint[:50] if chunk else "NAO ENCONTRADO"
    print(f"  [{cat:.10s} | conf={conf:.2f} | kb={score:.2f}] {text}")
    if chunk:
        print(f"    -> Chunk: {chunk_name}")
print()

# Teste 2: Simula conversa para ticket de documento
print("--- Simulacao de conversa (ticket: 'Incluir Documento') ---")

class FakeTicket:
    class FakeOrg:
        all = lambda self: []
    title = "Incluir Documento"
    description = "Preciso incluir um arquivo PDF no documento do sistema"
    organization = None
    id = "fake-id-123"
    priority = "MEDIUM"

    def __init__(self):
        self.organization = self.FakeOrg()
        # Evita queries reais
        from apps.tenants.models import Organization
        try:
            self.organization = Organization.objects.first()
        except:
            pass

    class messages:
        @staticmethod
        def filter(**kwargs):
            class EmptyQS:
                def order_by(self, *a): return self
                def first(self): return None
                def exists(self): return False
            return EmptyQS()

ticket = FakeTicket()

# Testa a funcao de busca diretamente
from apps.tickets.conversational_ai import _detect_category, _search_knowledge_base
combined = f"{ticket.title} {ticket.description}"
cat, conf = _detect_category(combined)
chunk, score = _search_knowledge_base(combined, cat)

print(f"  Categoria: {cat} (conf={conf:.2f})")
print(f"  KB score: {score:.2f}")
if chunk:
    print(f"  Chunk encontrado: {chunk.question_hint[:80]}")
    print(f"  Preview da resposta:\n    {chunk.content[:200]}")
print()

# Teste 3: Total de chunks por source
print("--- Chunks no banco por fonte ---")
from django.db.models import Count
for source in KnowledgeChunk.objects.values('source_name').annotate(total=Count('id')):
    print(f"  {source['source_name'][:60]}: {source['total']} chunks")

total = KnowledgeChunk.objects.filter(is_active=True).count()
print(f"\nTotal de chunks ativos: {total}")
print("\nTeste concluido!")
