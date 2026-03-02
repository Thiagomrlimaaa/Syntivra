"""
Ingestão COMPLETA dos PDFs do E-Palmas/SIGED no banco de dados do Syntivra.
Processa automaticamente todas as 249 páginas dos 3 manuais.

Estratégia de chunking:
  - Detecta seções/funcionalidades por padrões de título (2.1., 2.2., etc.)
  - Agrupa páginas sequenciais que pertencem à mesma seção
  - Gera keywords automaticamente por frequência de termos relevantes
  - Inicia cada chunk com uma pergunta-hint derivada do título da seção

Execute com:
  .\\venv\\Scripts\\python.exe ingest_knowledge_full.py
"""
import os, sys, re, django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, '.')
django.setup()

from apps.tickets.knowledge_models import KnowledgeChunk

# ─── Configuração dos PDFs ───────────────────────────────────────────────────
PDF_EXTRACTS = [
    {
        "file": "pdf_extract_PALMAS_GLOSSARIO.txt",
        "source_name": "Glossário SIGED - E-Palmas",
        "source_type": KnowledgeChunk.SourceType.PDF_MANUAL,
        "base_confidence": 0.98,
    },
    {
        "file": "pdf_extract_Manual___Modulo_Documentos.txt",
        "source_name": "Manual Módulo Documentos - E-Palmas v1.0",
        "source_type": KnowledgeChunk.SourceType.PDF_MANUAL,
        "base_confidence": 0.95,
    },
    {
        "file": "pdf_extract_Manual___Modulo_Processos.txt",
        "source_name": "Manual Módulo Processos - E-Palmas v1.0",
        "source_type": KnowledgeChunk.SourceType.PDF_MANUAL,
        "base_confidence": 0.95,
    },
]

# Stop words para extração de keywords
STOP_WORDS = {
    'o', 'a', 'os', 'as', 'um', 'uma', 'e', 'de', 'da', 'do', 'em', 'no',
    'na', 'que', 'para', 'por', 'com', 'ou', 'se', 'ao', 'aos', 'as', 'no',
    'na', 'nos', 'nas', 'este', 'esta', 'esse', 'essa', 'isso', 'aquele',
    'qual', 'quais', 'seu', 'sua', 'seus', 'suas', 'foi', 'ser', 'ter',
    'pode', 'são', 'está', 'também', 'mais', 'mas', 'não', 'sim', 'após',
    'antes', 'como', 'quando', 'onde', 'caso', 'seu', 'sua', 'desta',
    'deste', 'desta', 'pelo', 'pela', 'pelos', 'pelas', 'já', 'ainda',
    'entre', 'sobre', 'até', 'desde', 'durante', 'contra', 'seguir',
    'elaboração', 'ikhon', 'tecnologia', 'página', 'versão', 'manual',
    'usuario', 'usuário', 'sistema',
}

# Padrões de título de seção nos manuais
SECTION_PATTERNS = [
    r'^\d+\.\d+[\.\s]+[A-ZÁÉÍÓÚÃÕÂÊÔÇÜ][A-ZÁÉÍÓÚÃÕÂÊÔÇÜa-záéíóúãõâêôçü\s\-/]+$',
    r'^[A-ZÁÉÍÓÚÃÕÂÊÔÇÜ][A-ZÁÉÍÓÚÃÕÂÊÔÇÜ\s\-/]{5,}$',
    r'^\d+\s*[-–]\s*[A-ZÁÉÍÓÚÃÕÂÊÔÇÜ]',
    r'^AÇÃO:\s+',
    r'^BARRA DE AÇÃO:\s+',
    r'^TERMO\s+DEFINIÇÃO$',
    r'^[A-Z]\s*$',  # Letras do glossário
]

# Mapeamento de termos → categorias de keyword
KEYWORD_MAP = {
    'documento': 'documento, protocolo',
    'processo': 'processo',
    'tramitar': 'tramitar, tramitacao',
    'tramitação': 'tramitar, tramitacao',
    'arquivar': 'arquivar, arquivamento',
    'arquivamento': 'arquivar, arquivamento',
    'assinar': 'assinatura digital',
    'assinatura': 'assinatura digital',
    'digital': 'arquivo digital',
    'certificado': 'certificado digital',
    'expedir': 'expedicao, expedir',
    'expedição': 'expedicao, expedir',
    'cancelar': 'cancelar',
    'cancelamento': 'cancelar',
    'distribuir': 'distribuir, distribuicao',
    'distribuição': 'distribuir, distribuicao',
    'emprestar': 'emprestimo, emprestar',
    'empréstimo': 'emprestimo, emprestar',
    'pesquisa': 'pesquisa, busca',
    'pesquisar': 'pesquisa, busca',
    'cadastrar': 'cadastrar, registro',
    'cadastro': 'cadastrar, registro',
    'nup': 'nup, numero protocolo',
    'protocolo': 'nup, numero protocolo',
    'guia': 'guia, tramitacao',
    'sobrestar': 'sobrestar, sobrestamento',
    'palavra-chave': 'palavra-chave, busca',
    'relatório': 'relatorio, relatorios',
    'comentar': 'comentar, comentario',
    'volume': 'volume, processo',
    'apensar': 'apensar, juntada, anexar',
    'anexar': 'anexar, juntada',
    'juntar': 'juntar, juntada',
    'follow': 'followup, prazo, acompanhamento',
    'prazo': 'prazo, followup',
    'ficha': 'ficha acompanhamento, despacho',
    'despacho': 'despacho, ficha',
    'listagem': 'listagem, lista',
    'acesso': 'acesso, permissao, perfil',
    'perfil': 'perfil, permissao',
    'minuta': 'minuta, modelo',
    'etiqueta': 'etiqueta, imprimir',
    'requerimento': 'requerimento, cadastro externo',
    'metadado': 'metadado, informacao',
    'glossário': 'glossario, termos',
    'corrente': 'situacao, corrente',
    'arquivado': 'situacao, arquivado',
}


def normalize(text):
    """Normaliza texto: lowercase + remove acentos para comparação."""
    text = text.lower()
    for a, b in [('ã','a'),('â','a'),('á','a'),('à','a'),('ê','e'),('é','e'),
                 ('î','i'),('í','i'),('ô','o'),('ó','o'),('õ','o'),('ú','u'),
                 ('û','u'),('ü','u'),('ç','c')]:
        text = text.replace(a, b)
    return text


def extract_keywords(text, max_kw=12):
    """Extrai keywords relevantes do texto por frequência e mapeamento."""
    norm = normalize(text)
    words = re.findall(r'[a-z]{4,}', norm)
    freq = {}
    for w in words:
        if w not in STOP_WORDS:
            freq[w] = freq.get(w, 0) + 1

    # Palavras mais frequentes
    top_words = sorted(freq.items(), key=lambda x: -x[1])[:max_kw]
    base_kws = [w for w, _ in top_words]

    # Adiciona mapeamentos semânticos
    extra_kws = set()
    for term, mapped in KEYWORD_MAP.items():
        if normalize(term) in norm:
            extra_kws.update(mapped.split(', '))

    all_kws = list(dict.fromkeys(base_kws + list(extra_kws)))[:max_kw]
    return ', '.join(all_kws)


def build_question_hint(section_title, text):
    """Gera uma pergunta-hint a partir do título da seção."""
    title = section_title.strip().lower()

    hints = {
        'alterar': f'como alterar dados, como editar {title}',
        'arquivar': f'como arquivar, como desarquivar, como localizar {title} arquivado',
        'cadastro': f'como cadastrar, como registrar novo {title}',
        'cadastrar': f'como cadastrar, como criar novo {title}',
        'cancelar tramitação': 'como cancelar tramitação, como desfazer envio',
        'cancelar': f'como cancelar, como reativar {title}',
        'comentar': f'como comentar, como incluir comentário em {title}',
        'distribuir': f'como distribuir {title} para funcionário',
        'emprestar': f'como emprestar {title}, como registrar devolução',
        'expedir': f'como expedir {title}, como enviar para externo ou outra secretaria',
        'ficha': 'como gerar ficha de acompanhamento, como imprimir folha de despacho',
        'follow': 'como acompanhar prazos, como usar followup',
        'guias': 'como gerar guias de tramitação, remessa e expedição',
        'juntar': f'como juntar, anexar ou apensar {title}',
        'anexar': 'como anexar documento a processo',
        'listagem': 'como usar a listagem, quais ações estão disponíveis na listagem',
        'palavra-chave': 'como incluir palavra-chave, como usar palavras-chave para busca',
        'pesquisa avançada': 'como fazer pesquisa avançada, como filtrar documentos',
        'pesquisa simples': 'como fazer pesquisa simples, como buscar pelo nup',
        'receber tramitação': 'como receber tramitação, como confirmar recebimento',
        'receber distribuição': 'como receber distribuição, como aceitar documento distribuído',
        'relatórios': 'como gerar relatórios, quais relatórios estão disponíveis',
        'tramitar': 'como tramitar documento ou processo, como encaminhar para outro departamento',
        'volumes': 'como gerenciar volumes de processo, como abrir novo volume',
        'publicação': 'como registrar publicação de ato oficial',
        'palavra chave': 'como incluir palavra-chave, como usar palavras chave na busca',
        'arquivo digital': 'como incluir arquivo digital, como fazer upload de pdf',
        'assinatura digital': 'como assinar digitalmente, como usar certificado digital',
        'pré-cadastro': 'como fazer pré-cadastro, como fazer protocolo rápido no guichê',
        'modelos e minutas': 'como usar modelos e minutas, como criar modelo de documento',
        'sobrestar': 'como sobrestar, diferença entre sobrestar e arquivar',
        'juntar documento': 'como juntar documentos, como anexar documentos',
        'documento interno': 'como cadastrar documento interno, como registrar protocolo interno',
        'documento externo': 'como cadastrar documento externo, como registrar protocolo externo',
        'requerimento': 'como cadastrar requerimento, como solicitar serviço pelo portal',
        'expedi': 'como expedir, como enviar para fora da secretaria',
    }

    for key, hint in hints.items():
        if key in title or key in normalize(text[:200]):
            return hint

    return f'como usar {section_title.lower()}, procedimentos para {section_title.lower()}'


def is_section_header(line):
    """Verifica se a linha parece um cabeçalho de seção."""
    line = line.strip()
    if len(line) < 3 or len(line) > 120:
        return False
    for pattern in SECTION_PATTERNS:
        if re.match(pattern, line):
            return True
    return False


def clean_text(text):
    """Remove ruído do texto extraído pelo pdfplumber."""
    # Remove linhas de cabeçalho/rodapé repetitivas
    lines = text.split('\n')
    cleaned = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        # Pula linhas de cabeçalho/rodapé típicas dos manuais
        if re.match(r'^Manual do usu[aá]rio.*Vers[aã]o', stripped):
            continue
        if re.match(r'^Elabora[çc][aã]o:\s+IKHON', stripped):
            continue
        if re.match(r'^\[P[aá]gina \d+\]$', stripped):
            continue
        if stripped in ['memo', '1', '2', '3', '4', '1\r', '2\r']:
            continue
        cleaned.append(stripped)
    return '\n'.join(cleaned)


def chunk_text_by_sections(full_text, source_name, source_type, base_confidence):
    """
    Divide o texto completo em chunks por seção.
    Cada seção vira um KnowledgeChunk independente.
    """
    # Divide por páginas para contexto
    pages = re.split(r'\[P[aá]gina \d+\]', full_text)
    
    # Reconstrói o texto completo sem marcadores de página
    combined = '\n'.join(page for page in pages if page.strip())
    
    # Detecta seções pelo padrão numérico (2.1, 2.2, etc.) ou títulos em maiúsculas
    section_pattern = re.compile(
        r'(\d+\.\d+[\.\s]+'
        r'[A-ZÁÉÍÓÚÃÕÂÊÔÇÜ][A-ZÁÉÍÓÚÃÕÂÊÔÇÜa-záéíóúãõâêôçü\s\-/]+)'
        r'|'
        r'(^AÇÃO:\s+[^\n]+)'
        r'|'
        r'(^BARRA DE AÇÃO:\s+[^\n]+)'
        r'|'
        r'(^\d+\s*[-–]\s*[A-ZÁÉÍÓÚÃÕÂÊÔÇÜ][^\n]+)',
        re.MULTILINE
    )
    
    chunks = []
    lines = combined.split('\n')
    
    current_title = "Visão Geral"
    current_content = []
    
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        
        is_new_section = False
        
        # Detecta início de nova seção
        if re.match(r'^\d+\.\d+[\.\s]+[A-ZÁÉÍÓÚ]', stripped) and len(stripped) < 80:
            is_new_section = True
        elif re.match(r'^AÇÃO:\s+[A-Z]', stripped):
            is_new_section = True
        elif re.match(r'^BARRA DE AÇÃO:\s+[A-Z]', stripped):
            is_new_section = True
        elif re.match(r'^\d+\s*[-–]\s*(INTRODUÇÃO|MÓDULO|TECLAS|FECHAMENTO)', stripped):
            is_new_section = True
        elif (stripped.isupper() and len(stripped) > 5 and len(stripped) < 60
              and not any(c.isdigit() for c in stripped[:3])):
            # Título em maiúsculas sem números no início
            is_new_section = True
        
        if is_new_section:
            # Salva chunk anterior se tem conteúdo relevante
            content = clean_text('\n'.join(current_content))
            if len(content) > 150:
                chunks.append({
                    'title': current_title,
                    'content': content,
                })
            current_title = stripped
            current_content = []
        else:
            current_content.append(line)
    
    # Salva último chunk
    content = clean_text('\n'.join(current_content))
    if len(content) > 150:
        chunks.append({
            'title': current_title,
            'content': content,
        })
    
    return chunks


def ingest_from_file(config):
    """Processa um arquivo de extração de PDF e ingere no banco."""
    filepath = config['file']
    if not os.path.exists(filepath):
        print(f"  [SKIP] Arquivo não encontrado: {filepath}")
        return 0
    
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        full_text = f.read()
    
    print(f"\n  Processando: {config['source_name']}")
    print(f"  Tamanho: {len(full_text):,} chars")
    
    sections = chunk_text_by_sections(
        full_text,
        config['source_name'],
        config['source_type'],
        config['base_confidence']
    )
    
    print(f"  Seções detectadas: {len(sections)}")
    
    created = 0
    for section in sections:
        title = section['title']
        content = section['content']
        
        # Limita tamanho do chunk para performance de busca
        if len(content) > 3000:
            content = content[:3000] + "\n\n[...conteúdo adicional disponível no manual completo]"
        
        keywords = extract_keywords(f"{title} {content}")
        question_hint = build_question_hint(title, content)
        
        # Extrai referência de página do conteúdo se disponível
        page_ref = ""
        page_match = re.search(r'P[aá]gina\s+(\d+)', content)
        if page_match:
            page_ref = f"Pág. {page_match.group(1)}"
        
        KnowledgeChunk.objects.create(
            source_type=config['source_type'],
            source_name=config['source_name'],
            keywords=keywords,
            question_hint=question_hint,
            content=content,
            confidence_score=config['base_confidence'],
            page_reference=page_ref,
            is_active=True,
        )
        created += 1
        print(f"    [+] {title[:70]}")
    
    return created


def main():
    print("=" * 65)
    print("  INGESTÃO COMPLETA DE CONHECIMENTO — E-Palmas/SIGED")
    print("=" * 65)
    
    # Remove todos os chunks de PDF existentes para reingestão limpa
    old = KnowledgeChunk.objects.filter(
        source_type=KnowledgeChunk.SourceType.PDF_MANUAL
    )
    count_old = old.count()
    if count_old > 0:
        old.delete()
        print(f"\nRemovidos {count_old} chunks de PDF antigos.\n")
    
    total = 0
    for config in PDF_EXTRACTS:
        count = ingest_from_file(config)
        total += count
    
    # Mantém chunks de histórico de tickets (aprendizado)
    history_count = KnowledgeChunk.objects.filter(
        source_type=KnowledgeChunk.SourceType.TICKET_HISTORY
    ).count()
    
    print("\n" + "=" * 65)
    print(f"  Chunks de PDF criados:     {total}")
    print(f"  Chunks de histórico:       {history_count}")
    print(f"  Total ativo no banco:      {KnowledgeChunk.objects.filter(is_active=True).count()}")
    print("=" * 65)
    print("\n  Ingestão concluída com sucesso!")
    print("  A IA agora conhece toda a documentação do E-Palmas/SIGED.\n")


if __name__ == "__main__":
    main()
