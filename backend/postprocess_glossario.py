"""
Pós-processamento: melhora o Glossário (chunks por letra) 
e remove chunks com conteúdo muito pequeno ou genérico.
"""
import os, sys, re, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, '.')
django.setup()

from apps.tickets.knowledge_models import KnowledgeChunk

# ─── Remove chunks de glossário genéricos e recria por letra ────────────────

GLOSSARIO_SOURCE = "Glossário SIGED - E-Palmas"

# Deleta os chunks existentes do glossário
KnowledgeChunk.objects.filter(source_name=GLOSSARIO_SOURCE).delete()
print("Glossário anterior removido.")

# Lê o arquivo do glossário
with open("pdf_extract_PALMAS_GLOSSARIO.txt", "r", encoding="utf-8", errors="replace") as f:
    text = f.read()

# Cria um chunk único grande com todo o glossário de termos
glossario_chunks = [
    {
        "keywords": "nup, numero protocolo, numero unico, protocolo, identificador",
        "question_hint": "o que é NUP, o que significa número único de protocolo, como funciona o NUP",
        "content": (
            "**NUP — Número Único de Protocolo**\n\n"
            "Conjunto numérico sequencial e único que fornece informações sobre a origem do protocolo, "
            "autenticidade, tipo, sequencial e ano de produção.\n\n"
            "- Documentos: NUP com **.9.** antes do sequencial. Ex: 00000.**9**.000058/2024\n"
            "- Processos: NUP com **.0.** antes do sequencial. Ex: 00000.**0**.000001/2024\n\n"
            "O NUP é o principal identificador para qualquer ação no sistema: tramitar, arquivar, pesquisar, "
            "expedir, assinar etc. **Guarde sempre o NUP após cadastrar um documento ou processo!**"
        ),
        "confidence": 0.99,
    },
    {
        "keywords": "acervo, arquivo, documento, guarda, colecao",
        "question_hint": "o que é acervo documental, o que é arquivo, diferença entre acervo e arquivo",
        "content": (
            "**Termos do Glossário SIGED — Acervo, Arquivo e Arquivar:**\n\n"
            "**Acervo documental**: Agrupamento de todos os documentos referentes a uma questão específica, "
            "ou documentos de uma entidade produtora/custodiadora.\n\n"
            "**Arquivo**: Conjunto de documentos produzidos e acumulados por uma entidade coletiva, "
            "pública ou privada, pessoa ou família, no desempenho de suas atividades. Independe do suporte.\n\n"
            "**Arquivar**: 1. Sequência de operações que visam à guarda ordenada de documentos. "
            "2. Ação pela qual uma autoridade determina a guarda de um documento, cessada a sua tramitação."
        ),
        "confidence": 0.97,
    },
    {
        "keywords": "assinatura digital, autenticidade, certificado digital, documento digital",
        "question_hint": "o que é assinatura digital, como funciona a assinatura digital no epalmas",
        "content": (
            "**Termos do Glossário SIGED — Assinatura e Documento Digital:**\n\n"
            "**Assinatura Digital**: Assinatura em meio eletrônico que permite aferir a origem e a integridade "
            "do documento. No E-Palmas pode ser feita via Certificado Digital (token) ou via Login e Senha.\n\n"
            "**Documento digital**: Documento codificado em dígitos binários, acessível por meio de sistema "
            "computacional.\n\n"
            "**Documento interno**: Produzido no âmbito da instituição, recebe NUP automaticamente.\n\n"
            "**Documento externo**: Não produzido internamente. Registrado em unidade protocolizadora "
            "ao ser recebido, também recebe NUP interno para tramite."
        ),
        "confidence": 0.97,
    },
    {
        "keywords": "tramitar, tramitacao, curso, movimentacao, tramite, envio",
        "question_hint": "o que é tramitação, o que significa tramitar um documento, o que é trâmite",
        "content": (
            "**Termos do Glossário SIGED — Tramitação e Movimentação:**\n\n"
            "**Tramitação**: Curso do documento desde a sua produção ou recepção até o cumprimento de sua "
            "função administrativa. Também chamado movimentação ou trâmite.\n\n"
            "**Distribuir**: Movimentar protocolos/documentos dentro do mesmo departamento, atribuindo "
            "responsabilidade a um funcionário. O documento continua na carga do departamento.\n\n"
            "**Expedir**: Ato de remeter documentos oficiais para uma determinada instituição ou pessoa "
            "externa, mediante registro de protocolo.\n\n"
            "**Carga (no sistema)**: Define a localização e responsabilidade de guarda atual dos protocolos. "
            "Ex.: 'Na carga do departamento X', o protocolo consta nas listagens da unidade."
        ),
        "confidence": 0.97,
    },
    {
        "keywords": "situacao, status, corrente, arquivado, sobrestado, expedido, cancelado",
        "question_hint": "quais são as situações de um documento no epalmas, o que significa corrente arquivado sobrestado expedido",
        "content": (
            "**Situações de um protocolo no E-Palmas (SIGED):**\n\n"
            "| Situação | Significado |\n"
            "|---|---|\n"
            "| **Corrente** | Em tramitação ativa, uso administrativo frequente |\n"
            "| **Arquivado** | Guardado (tramitação encerrada), ainda acessível |\n"
            "| **Sobrestado** | Suspenso temporariamente aguardando providência |\n"
            "| **Expedido** | Enviado para instância externa |\n"
            "| **Cancelado** | Cancelado (sem validade), NUP não é apagado |\n"
            "| **Tramitando** | Em movimento entre departamentos |\n\n"
            "**Sobrestar**: Suspensão temporária de ações para um protocolo que aguarda alguma providência "
            "(envio de outros documentos, decisão, pesquisa, prazos). Diferente do arquivamento, "
            "que é guarda definitiva após encerramento."
        ),
        "confidence": 0.99,
    },
    {
        "keywords": "perfil, usuario, permissao, acesso, administrador, tecnico, protocolo",
        "question_hint": "quais são os perfis de usuário no epalmas, o que é perfil de sistema, não consigo acessar funcionalidade",
        "content": (
            "**Perfis de Usuário no E-Palmas (SIGED):**\n\n"
            "O Perfil determina as permissões e acessos de cada usuário:\n\n"
            "- **Administrador/Gestor**: Acesso completo, inclui configurações, manutenção e ações "
            "exclusivas de gestão;\n"
            "- **Técnico/Analista**: Acesso às funcionalidades operacionais do módulo;\n"
            "- **Protocolo**: Atendimento em guichê, pré-cadastro e cadastro de documentos externos;\n"
            "- **Usuário externo**: Acesso ao portal para protocolar documentos sem ser servidor interno.\n\n"
            "Se uma funcionalidade não aparece no menu, verifique seu perfil com o administrador do sistema.\n\n"
            "**Carga e acesso**: A carga define quais protocolos o usuário/departamento pode ver e "
            "operar. Documentos fora da carga do departamento têm acesso restrito."
        ),
        "confidence": 0.97,
    },
    {
        "keywords": "classificacao arquivistica, prazo guarda, plano classificacao, metadado",
        "question_hint": "o que é classificação arquivística, para que serve, o que é prazo de guarda",
        "content": (
            "**Termos do Glossário — Classificação e Metadados:**\n\n"
            "**Classificação arquivística**: Análise e identificação do conteúdo de documentos. "
            "Organiza os documentos de acordo com um plano de classificação e código, "
            "determina o prazo de guarda e estabelece a destinação final.\n\n"
            "**Prazo de guarda**: Prazo definido na tabela de temporalidade, baseado em estimativas de uso, "
            "durante o qual os documentos devem ser mantidos no arquivo corrente ou intermediário.\n\n"
            "**Metadados**: Dados estruturados e codificados que descrevem, permitem acessar, gerenciar e "
            "preservar outros dados ao longo do tempo. Ex.: NUP, data, tipo documental, assunto, interessado.\n\n"
            "**Atributo**: Característica específica atribuída a um tipo documental, constitui um metadado "
            "desse tipo. Campos complementares ativados conforme preenchimento de outros campos."
        ),
        "confidence": 0.95,
    },
    {
        "keywords": "fluxo trabalho, workflow, automatico, processo automatizado",
        "question_hint": "o que é fluxo de trabalho no epalmas, como funciona o workflow automático",
        "content": (
            "**Fluxo de Trabalho (Workflow) no E-Palmas:**\n\n"
            "1. Agrupamento de atividades funcionais que trata o movimento de informação entre elas, "
            "mostrando a relação de cada atividade com as demais realizadas no grupo.\n\n"
            "2. Sequência de passos necessários para automatizar processos de negócio, de acordo com "
            "um conjunto de regras definidas, permitindo que sejam transmitidos de uma pessoa para outra.\n\n"
            "No E-Palmas, o Módulo Documentos permite inserir documentos em fluxos automáticos de trabalho "
            "via a opção **'Fluxo de Trabalho'** na listagem."
        ),
        "confidence": 0.92,
    },
    {
        "keywords": "follow up, prazo, acompanhamento, vencimento, prazo resposta",
        "question_hint": "o que é follow-up no epalmas, como acompanhar prazos de resposta",
        "content": (
            "**Follow-up no E-Palmas:**\n\n"
            "Funcionalidade destinada ao acompanhamento dos prazos de resposta estabelecidos para "
            "processos/documentos tramitados.\n\n"
            "- Lista os protocolos cujos prazos venceram, vencem hoje ou irão vencer;\n"
            "- **Processos em vermelho** = prazos vencidos;\n"
            "- Para 'dar baixa' no prazo: o departamento de destino deve RECEBER A TRAMITAÇÃO e realizar "
            "uma NOVA TRAMITAÇÃO de volta para o departamento que solicitou o prazo;\n"
            "- Acesse: **Módulo Processos ou Documentos → Follow-up**."
        ),
        "confidence": 0.95,
    },
    {
        "keywords": "guia, tramitacao, remessa, expedicao, controle envio, comprovante",
        "question_hint": "o que são guias no epalmas, como gerar guia de tramitação remessa expedição",
        "content": (
            "**Guias no E-Palmas (SIGED):**\n\n"
            "Formulários físicos ou digitais para registro de movimentação de protocolos, "
            "que atestam o envio e o recebimento, registrando metadados como datas e responsáveis.\n\n"
            "**Tipos de Guias disponíveis:**\n"
            "- **Guia de Tramitação**: Controle de processos tramitados entre departamentos;\n"
            "- **Guia de Remessa**: Controle do envio de malotes de remessa;\n"
            "- **Guia de Expedição Externo**: Controle de envio para externos à instituição;\n"
            "- **Guia de Expedição Outras Secretarias**: Controle entre secretarias;\n"
            "- **Guia de Expedição Em Mãos**: Controle de entrega física em mãos.\n\n"
            "Acesse: **Módulo Processos/Documentos → Guias**."
        ),
        "confidence": 0.95,
    },
    {
        "keywords": "juntada, anexar, apensar, juntar documento, juntar processo",
        "question_hint": "o que é juntada, diferença entre anexação e apensação, como juntar documentos",
        "content": (
            "**Juntada, Anexação e Apensação no E-Palmas:**\n\n"
            "**Juntada**: Junção de documentos/processos a outros documentos/processos.\n\n"
            "**Diferença entre Anexação e Apensação:**\n"
            "- **Anexação**: O documento/processo anexado passa a integrar definitivamente o principal;\n"
            "- **Apensação**: União temporária/provisória, mantendo a autonomia jurídica de cada um;\n"
            "- Para documentos juntados a processos: apenas **Anexação** é permitida.\n\n"
            "**Para desfazer:**\n"
            "- **Desmembrar**: Retira e permite reutilizar em outros processos;\n"
            "- **Desentranhar**: Retira e deixa na listagem de correntes para uso futuro.\n\n"
            "Acesse: **Módulo Processos → Anexar/Apensar** ou **Módulo Documentos → Juntar Documento**."
        ),
        "confidence": 0.97,
    },
    {
        "keywords": "cancelamento, reativar, validade, desfazer cancelamento",
        "question_hint": "o que é cancelamento de documento, como reativar documento cancelado, o que acontece ao cancelar",
        "content": (
            "**Cancelamento no E-Palmas:**\n\n"
            "O cancelamento é a ação que **retira a validade probatória** do documento e a validade "
            "do NUP associado.\n\n"
            "- O NUP cancelado **não desaparece** do sistema — fica com status 'CANCELADO';\n"
            "- Para acessar: selecione a situação **'CANCELADO'** na Listagem;\n"
            "- Pode ser revertido usando a ação **'RECUPERAR DOCUMENTO'** (Reativar);\n\n"
            "**Cancelar Tramitação** (diferente de Cancelar Documento):\n"
            "- Cancela apenas o movimento (tramitação) ainda não recebida pelo destino;\n"
            "- Só pode ser feito pelo departamento que realizou a tramitação;\n"
            "- Após cancelar, o documento volta para Listagem de correntes do remetente."
        ),
        "confidence": 0.97,
    },
    {
        "keywords": "emprestimo, emprestar, devolver, arquivo consultado, sobrestado",
        "question_hint": "o que é empréstimo de processo, como emprestar um documento, diferença empréstimo e tramitação",
        "content": (
            "**Empréstimo no E-Palmas:**\n\n"
            "O empréstimo registra que o processo/documento foi retirado do arquivo do departamento "
            "para consulta por um usuário de outro departamento.\n\n"
            "**Diferença entre Empréstimo e Tramitação:**\n"
            "- **Tramitação**: Transfere a carga (responsabilidade) do departamento;\n"
            "- **Empréstimo**: Não altera o departamento de carga, apenas a situação do protocolo.\n\n"
            "O empréstimo só é possível em protocolos com situação **'ARQUIVADO'** ou **'SOBRESTADO'**.\n\n"
            "**Para devolver**: Acione o botão **'DEVOLVER'** — o sistema altera o campo Ativo de SIM para NÃO.\n\n"
            "Acesse: **Módulo Processos/Documentos → Emprestar**."
        ),
        "confidence": 0.96,
    },
]

created = 0
for chunk_data in glossario_chunks:
    KnowledgeChunk.objects.create(
        source_type=KnowledgeChunk.SourceType.PDF_MANUAL,
        source_name=GLOSSARIO_SOURCE,
        keywords=chunk_data["keywords"],
        question_hint=chunk_data["question_hint"],
        content=chunk_data["content"],
        confidence_score=chunk_data["confidence"],
        page_reference="Glossário SIGED",
        is_active=True,
    )
    created += 1
    print(f"  [OK] {chunk_data['question_hint'][:70]}")

print(f"\nGlossário: {created} chunks criados.")
total = KnowledgeChunk.objects.filter(is_active=True).count()
print(f"Total geral de chunks ativos: {total}")
print("\nPós-processamento concluído!")
