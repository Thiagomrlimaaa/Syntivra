"""
Script para ensinar a IA a usar o Padrão de Resposta Oficial de Suporte.
Atualiza os chunks procedimentais (passo a passo) para o novo formato:

- Resposta direta (1 linha): Para [ação], faça o seguinte:
- Passo a passo objetivo e limpo (Passo 1, Passo 2...)
- Encerramento simples: Pronto. [Ação] será concluída.
"""
import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, '.')
django.setup()

from apps.tickets.knowledge_models import KnowledgeChunk
from django.db.models import Q

# Lista de reescritas com o padrão oficial rígido solicitado pelo C-Level/Admin
REWRITES = [
    {
        "match_title": ["Tramitar", "tramitacao", "tramitação"],
        "content": (
            "Para tramitar um documento ou processo, faça o seguinte:\n\n"
            "Acesse o menu Documentos ou Processos.\n"
            "Localize o protocolo na listagem.\n"
            "Clique na ação Tramitar.\n"
            "Informe o setor de destino.\n"
            "Adicione o motivo da tramitação (se necessário).\n"
            "Clique em Confirmar.\n\n"
            "Pronto. O processo será enviado ao setor informado.\n"
            "Se aparecer em vermelho na listagem, significa que ainda não foi recebido pelo setor."
        )
    },
    {
        "match_title": ["Arquivo Digital", "upload", "incluir arquivo", "anexar pdf"],
        "content": (
            "Para incluir um arquivo digital, faça o seguinte:\n\n"
            "Acesse o Módulo Documentos.\n"
            "Clique em Arquivo Digital.\n"
            "Informe o número do NUP.\n"
            "Clique em Pesquisar.\n"
            "Clique em Escolher Arquivo e selecione o PDF (apenas formato PDF é aceito).\n"
            "Clique em Anexar.\n\n"
            "Pronto. O arquivo digital será adicionado ao documento."
        )
    },
    {
        "match_title": ["Arquivar", "desarquivar"],
        "content": (
            "Para arquivar um documento ou processo, faça o seguinte:\n\n"
            "Acesse o menu Arquivar.\n"
            "Informe o número do protocolo (NUP) e pesquise.\n"
            "Informe a caixa ou localização física do documento.\n"
            "Clique na opção Arquivar.\n\n"
            "Pronto. O protocolo mudará para a situação Arquivado."
        )
    },
    {
        "match_title": ["Assinatura Digital", "assinar", "certificado digital"],
        "content": (
            "Para assinar digitalmente um documento, faça o seguinte:\n\n"
            "Acesse o Módulo Documentos.\n"
            "Vá em Arquivo Digital, informe o NUP e pesquise.\n"
            "Clique no botão Assinatura Digital.\n"
            "Selecione Através de Login e Senha ou Certificado Digital (Token).\n"
            "Digite sua senha (se via login) ou o pin (se via token).\n"
            "Clique em Assinar.\n\n"
            "Pronto. O arquivo receberá um QR Code de autenticidade."
        )
    },
    {
        "match_title": ["Cadastrar Documento", "cadastrar processo"],
        "content": (
            "Para cadastrar um novo documento ou processo, faça o seguinte:\n\n"
            "Acesse o menu Cadastrar.\n"
            "Selecione o tipo do protocolo (Interno ou Externo).\n"
            "Preencha todos os campos obrigatórios marcados com asterisco vermelho (ex: Assunto, Interessado).\n"
            "Clique em Incluir no fim da página.\n\n"
            "Pronto. O sistema vai registrar e gerar um NUP (Número Único de Protocolo) automaticamente."
        )
    },
    {
        "match_title": ["Cancelar Tramitação", "cancelamento"],
        "content": (
            "Para cancelar uma tramitação, faça o seguinte:\n\n"
            "Acesse a Listagem de processos do seu departamento.\n"
            "Localize o processo que foi enviado, mas ainda não foi recebido (aparece em vermelho).\n"
            "Clique em Cancelar na barra de ações.\n"
            "Confirme a ação.\n\n"
            "Pronto. O processo não irá mudar de departamento e voltará para a sua carga."
        )
    },
    {
        "match_title": ["Distribuir", "distribuição"],
        "content": (
            "Para distribuir um protocolo a um funcionário do setor, faça o seguinte:\n\n"
            "Acesse a Listagem e localize o processo.\n"
            "Clique na ação Distribuir.\n"
            "Selecione qual funcionário ficará responsável.\n"
            "Preencha o motivo da distribuição.\n"
            "Clique em Confirmar.\n\n"
            "Pronto. A responsabilidade do processo será do funcionário selecionado."
        )
    },
    {
        "match_title": ["Expedir", "guia de expedicao", "expedição externa"],
        "content": (
            "Para expedir um documento para um órgão externo, faça o seguinte:\n\n"
            "Acesse o menu Expedir.\n"
            "Informe o NUP e pesquise.\n"
            "Selecione o Destinatário externo.\n"
            "Clique em Gerar Guia (opcional).\n"
            "Clique em Expedir.\n\n"
            "Pronto. O registro da remessa será guardado no sistema e o protocolo atualiza para Expedido."
        )
    },
    {
        "match_title": ["Anexar / Apensar", "juntada", "desmembrar"],
        "content": (
            "Para anexar ou apensar um documento a outro processo, faça o seguinte:\n\n"
            "Acesse o menu Anexar / Apensar.\n"
            "Informe o NUP do processo principal.\n"
            "Clique no botão de adição (+).\n"
            "Insira o NUP do documento secundário.\n"
            "Clique em Anexar ou Apensar.\n\n"
            "Pronto. A juntada das peças será concluída no sistema."
        )
    },
    {
        "match_title": ["Pesquisa Avançada", "pesquisa simples"],
        "content": (
            "Para buscar um documento que você não possui o NUP completo, faça o seguinte:\n\n"
            "Acesse o menu Pesquisa Avançada.\n"
            "Preencha os campos que você sabe do processo (Interessado, Assunto ou Data).\n"
            "Clique em Pesquisar.\n\n"
            "Pronto. A listagem exibirá todos os resultados encontrados no sistema."
        )
    },
    {
        "match_title": ["Receber", "Receber Tramitação", "receber distribuição"],
        "content": (
            "Para receber um processo enviado ao seu setor, faça o seguinte:\n\n"
            "Acesse a Listagem do departamento.\n"
            "Localize os processos que aparecerão destacados em vermelho.\n"
            "Clique na caixa de seleção ao lado de cada processo.\n"
            "Clique no botão Receber na barra de ação superior.\n\n"
            "Pronto. O processo constará oficialmente na carga do seu departamento."
        )
    },
    {
        "match_title": ["FollowUp", "follow-up", "prazo"],
        "content": (
            "Para acompanhar protocolos com prazos de resposta, faça o seguinte:\n\n"
            "Acesse o menu Follow Up.\n"
            "Observe as cores na lista: registros em vermelho estão vencidos.\n"
            "Verifique os registros em aberto que vão vencer.\n\n"
            "Pronto. O acompanhamento dos prazos pendentes do departamento será exibido."
        )
    }
]

def apply_format():
    print("Aplicando Padrão de Resposta Objetiva na IA...\n")
    updated = 0
    not_updated = 0

    chunks = KnowledgeChunk.objects.filter(is_active=True)

    for chunk in chunks:
        # Verifica se alguma reescrita mapeada bate com a keyword ou o título do chunk
        matched = False
        for rule in REWRITES:
            # Compara título ou keywords para injetar a resposta perfeita
            if any(term.lower() in chunk.keywords.lower() or term.lower() in chunk.question_hint.lower() for term in rule["match_title"]):
                # Substitui o conteúdo original (textão do manual) pela versão padronizada do C-Level
                chunk.content = rule["content"]
                chunk.save()
                updated += 1
                matched = True
                break
        
        # Se for um chunk procedimental (pelo título), mas não estiver no REWRITES, aplica filtro automático leve
        if not matched and "como" in chunk.question_hint.lower():
            # Tenta pegar as primeiras frases do manual e adicionar "Siga estes passos:"
            clean_text = chunk.content.replace("A funcionalidade", "A ação")
            
            # Se a linha contiver "Procedimentos:", cortamos toda a enrolação anterior!
            if "Procedimentos:" in clean_text:
                parts = clean_text.split("Procedimentos:")
                auto_format = "Siga estes passos:\n\n" + parts[1].strip().replace("▪", "•")
                chunk.content = auto_format
                chunk.save()
                updated += 1
                matched = True
            
            if not matched:
                not_updated += 1

    print(f"Chunks com padrão humano/direto aplicado: {updated}.")
    print(f"Chunks sem padronização automatica (mantidos texto PDF): {not_updated}.")

if __name__ == "__main__":
    apply_format()
