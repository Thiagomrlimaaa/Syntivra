import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, '.')
django.setup()

from apps.tickets.knowledge_models import KnowledgeChunk

# Lista de reescritas com o padrão oficial rígido solicitado pelo C-Level/Admin (com Markdown e quebras corretas)
REWRITES = [
    {
        "match_title": ["Tramitar", "tramitacao", "tramitação"],
        "content": (
            "Para tramitar um documento ou processo, faça o seguinte:\n\n"
            "1. Acesse o menu **Documentos** ou **Processos**.\n"
            "2. Localize o protocolo na listagem.\n"
            "3. Clique em **Tramitar**.\n"
            "4. Informe o setor de destino.\n"
            "5. Adicione o motivo (se necessário).\n"
            "6. Selecione **Tramitar sem arquivo** e clique em **Tramitar**.\n\n"
            "Pronto. O processo será enviado ao setor informado.\n\n"
            "Se aparecer em vermelho, significa que ainda não foi recebido pelo setor."
        )
    },
    {
        "match_title": ["Arquivo Digital", "upload", "incluir arquivo", "anexar pdf"],
        "content": (
            "Para incluir um arquivo digital, faça o seguinte:\n\n"
            "1. Acesse o Módulo **Documentos**.\n"
            "2. Clique em **Arquivo Digital**.\n"
            "3. Informe o número do NUP.\n"
            "4. Clique em **Pesquisar**.\n"
            "5. Clique em **Escolher Arquivo** e selecione o PDF (apenas formato PDF é aceito).\n"
            "6. Clique em **Anexar**.\n\n"
            "Pronto. O arquivo digital será adicionado ao documento."
        )
    },
    {
        "match_title": ["Arquivar", "desarquivar"],
        "content": (
            "Para arquivar um processo, faça o seguinte:\n\n"
            "1. Acesse o processo na sua listagem.\n"
            "2. Clique na opção **Arquivar**.\n"
            "3. Preencha os campos obrigatórios.\n"
            "4. Clique em **Confirmar**.\n\n"
            "Pronto. O processo ficará arquivado no seu setor."
        )
    },
    {
        "match_title": ["Assinatura Digital", "assinar", "certificado digital"],
        "content": (
            "Para assinar digitalmente um documento, faça o seguinte:\n\n"
            "1. Acesse o Módulo **Documentos**.\n"
            "2. Vá em **Arquivo Digital**, informe o NUP e pesquise.\n"
            "3. Clique no botão **Assinatura Digital**.\n"
            "4. Selecione **Através de Login e Senha** ou **Certificado Digital (Token)**.\n"
            "5. Digite sua senha (se via login) ou o pin (se via token).\n"
            "6. Clique em **Assinar**.\n\n"
            "Pronto. O arquivo receberá um QR Code de autenticidade."
        )
    },
    {
        "match_title": ["Cadastrar Documento", "cadastrar processo"],
        "content": (
            "Para cadastrar um novo documento ou processo, faça o seguinte:\n\n"
            "1. Acesse o menu **Cadastrar**.\n"
            "2. Selecione o tipo do protocolo (**Interno** ou **Externo**).\n"
            "3. Preencha todos os campos obrigatórios (ex: Assunto, Interessado).\n"
            "4. Clique em **Incluir** no fim da página.\n\n"
            "Pronto. O sistema vai registrar e gerar um NUP automaticamente."
        )
    },
    {
        "match_title": ["Cancelar Tramitação", "cancelamento"],
        "content": (
            "Para cancelar uma tramitação, faça o seguinte:\n\n"
            "1. Acesse a Listagem de processos do seu departamento.\n"
            "2. Localize o processo que foi enviado, mas ainda não foi recebido (aparece em vermelho).\n"
            "3. Clique em **Cancelar** na barra de ações.\n"
            "4. Confirme a ação.\n\n"
            "Pronto. O processo não irá mudar de departamento e voltará para a sua carga."
        )
    },
    {
        "match_title": ["Distribuir", "distribuição"],
        "content": (
            "Para distribuir um protocolo a um funcionário do setor, faça o seguinte:\n\n"
            "1. Acesse a Listagem e localize o processo.\n"
            "2. Clique na ação **Distribuir**.\n"
            "3. Selecione qual funcionário ficará responsável.\n"
            "4. Preencha o motivo da distribuição.\n"
            "5. Clique em **Confirmar**.\n\n"
            "Pronto. A responsabilidade do processo será do funcionário selecionado."
        )
    },
    {
        "match_title": ["Expedir", "guia de expedicao", "expedição externa"],
        "content": (
            "Para expedir um documento para um órgão externo, faça o seguinte:\n\n"
            "1. Acesse o menu **Expedir**.\n"
            "2. Informe o NUP e pesquise.\n"
            "3. Selecione o Destinatário externo.\n"
            "4. Clique em **Gerar Guia** (opcional).\n"
            "5. Clique em **Expedir**.\n\n"
            "Pronto. O registro da remessa será guardado no sistema e o protocolo atualiza para Expedido."
        )
    },
    {
        "match_title": ["Anexar / Apensar", "juntada", "desmembrar"],
        "content": (
            "Para anexar ou apensar um documento a outro processo, faça o seguinte:\n\n"
            "1. Acesse o menu **Anexar / Apensar**.\n"
            "2. Informe o NUP do processo principal.\n"
            "3. Clique no botão de adição **(+)**.\n"
            "4. Insira o NUP do documento secundário.\n"
            "5. Clique em **Anexar** ou **Apensar**.\n\n"
            "Pronto. A juntada das peças será concluída no sistema."
        )
    },
    {
        "match_title": ["Pesquisa Avançada", "pesquisa simples"],
        "content": (
            "Para buscar um documento que você não possui o NUP completo, faça o seguinte:\n\n"
            "1. Acesse o menu **Pesquisa Avançada**.\n"
            "2. Preencha os campos que você sabe do processo (Interessado, Assunto ou Data).\n"
            "3. Clique em **Pesquisar**.\n\n"
            "Pronto. A listagem exibirá todos os resultados encontrados no sistema."
        )
    },
    {
        "match_title": ["Receber", "Receber Tramitação", "receber distribuição"],
        "content": (
            "Para receber um processo enviado ao seu setor, faça o seguinte:\n\n"
            "1. Acesse a Listagem do departamento.\n"
            "2. Localize os processos que aparecerão destacados em vermelho.\n"
            "3. Clique na caixa de seleção ao lado de cada processo.\n"
            "4. Clique no botão **Receber** na barra de ação superior.\n\n"
            "Pronto. O processo constará oficialmente na carga do seu departamento."
        )
    },
    {
        "match_title": ["FollowUp", "follow-up", "prazo"],
        "content": (
            "Para acompanhar protocolos com prazos de resposta, faça o seguinte:\n\n"
            "1. Acesse o menu **Follow Up**.\n"
            "2. Observe as cores na lista: registros em vermelho estão vencidos.\n"
            "3. Verifique os registros em aberto que vão vencer.\n\n"
            "Pronto. O acompanhamento dos prazos pendentes do departamento será exibido."
        )
    }
]

def apply_format():
    print("Aplicando Padrão de Resposta Objetiva na IA...\n")
    updated = 0

    chunks = KnowledgeChunk.objects.filter(is_active=True)

    for chunk in chunks:
        # Verifica se alguma reescrita mapeada bate com a keyword ou o título do chunk
        for rule in REWRITES:
            if any(term.lower() in chunk.keywords.lower() or term.lower() in chunk.question_hint.lower() for term in rule["match_title"]):
                chunk.content = rule["content"]
                chunk.save()
                updated += 1
                break

    print(f"Chunks com padrão humano/direto aplicado: {updated}.")

if __name__ == "__main__":
    apply_format()
