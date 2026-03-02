import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, '.')
django.setup()

from apps.tickets.conversational_ai import _detect_category, _search_knowledge_base
from apps.tickets.knowledge_models import KnowledgeChunk
from django.db.models import Count

perguntas = [
    "Incluir documento no sistema",
    "Como tramitar processo para outra secretaria",
    "Expedir processo para externo",
    "Nao consigo arquivar o processo",
    "Como fazer assinatura digital com certificado",
    "O que e NUP",
    "Como usar o follow-up",
    "Quero gerar guia de tramitacao",
    "Como anexar processo a outro processo",
    "Nao tenho permissao para acessar a tela",
    "Como sobrestar um documento",
    "Quero cancelar tramitacao",
    "Como receber tramitacao",
    "Como usar palavra chave para busca",
    "Gerar relatorio de producao documental",
    "Como abrir novo volume de processo",
    "Como fazer pesquisa avancada",
    "Como distribuir processo para funcionario",
    "Como desfazer juntada de documentos",
    "O que e follow up de prazos",
]

print("COBERTURA DA BASE DE CONHECIMENTO:")
print("=" * 70)
found = 0
for q in perguntas:
    cat, conf = _detect_category(q)
    chunk, score = _search_knowledge_base(q, cat)
    status = "[OK]" if score > 0.3 else "[??]"
    if score > 0.3:
        found += 1
    chunk_hint = chunk.question_hint[:45] if chunk else "SEM RESULTADO"
    print(f"  {status} [{cat:.10s}|{score:.2f}] {q[:35]:<35} -> {chunk_hint}")

print()
print(f"Cobertura: {found}/{len(perguntas)} ({100*found//len(perguntas)}%)")
print(f"Total chunks no banco: {KnowledgeChunk.objects.filter(is_active=True).count()}")

print()
print("Chunks por fonte:")
for s in KnowledgeChunk.objects.values("source_name").annotate(t=Count("id")).order_by("-t"):
    print(f"  {s['source_name'][:60]}: {s['t']} chunks")
