"""
Script de ingestão dos PDFs do E-Palmas/SIGED no banco de dados do Syntivra.
Extrai, segmenta e indexa o conhecimento dos manuais como KnowledgeChunks.

Execute com:
  .\\venv\\Scripts\\python.exe ingest_knowledge.py
"""
import os, sys, django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, '.')
django.setup()

import pdfplumber
from apps.tickets.knowledge_models import KnowledgeChunk

PDF_DIR = r"C:\Users\AVELL\Documents\Syntivra"

# ─── Chunks estáticos estruturados extraídos dos PDFs ────────────────────────
# Cada chunk tem: keywords, question_hint, content, confidence, page_reference
MANUAL_CHUNKS = [

    # ── MÓDULO DOCUMENTOS ────────────────────────────────────────────────────

    {
        "source_name": "Manual Módulo Documentos - E-Palmas v1.0",
        "keywords": "incluir, arquivo digital, documento, upload, pdf, anexar, nup, protocolo",
        "question_hint": "como incluir arquivo digital, como anexar pdf, como fazer upload de arquivo no documento",
        "content": (
            "Para incluir um Arquivo Digital a um documento no E-Palmas, siga os passos:\n\n"
            "1. Acesse o menu **Módulo Documentos → Arquivo Digital**;\n"
            "2. No campo NUP, informe o número do documento ao qual deseja inserir o arquivo;\n"
            "3. Acione o botão **'PESQUISAR'**;\n"
            "4. Clique em **'ESCOLHER ARQUIVO'** para localizar o arquivo no seu computador;\n"
            "   ⚠️ O sistema aceita **apenas arquivos no formato PDF**;\n"
            "5. Selecione o arquivo desejado e clique em **'ABRIR'**;\n"
            "6. Acione o botão **'ANEXAR'** para carregar o arquivo;\n"
            "7. O sistema atualizará a página confirmando o upload.\n\n"
            "**Importante:** Somente o usuário que incluiu o arquivo pode excluí-lo, e apenas até a próxima tramitação."
        ),
        "confidence": 0.95,
        "page": "Pág. 11-12",
    },
    {
        "source_name": "Manual Módulo Documentos - E-Palmas v1.0",
        "keywords": "cadastrar documento interno, documento geral, nup, protocolo, cadastro",
        "question_hint": "como cadastrar documento interno, como registrar novo documento, como criar protocolo",
        "content": (
            "Para **Cadastrar um Documento Interno** no E-Palmas:\n\n"
            "1. Acesse **Módulo Documentos → Cadastrar Documento Interno → Cadastrar Documento Geral**;\n"
            "2. Preencha o formulário com as informações do documento (campos com **asterisco vermelho são obrigatórios**):\n"
            "   - **Número do Documento**: numeração de controle (ex: Ofício 35/2024). Use S/N se não houver;\n"
            "   - **Data do Documento**: data de criação/assinatura;\n"
            "   - **Tipo Documental**: estrutura do documento (carta, ofício, memorando etc.);\n"
            "   - **Acesso**: Público ou Sigiloso;\n"
            "   - **Classificação Arquivística**: organiza o documento e define prazos de guarda;\n"
            "   - **Assunto**: descrição do conteúdo;\n"
            "   - **Interessado**: pessoa(s) interessada(s) no documento;\n"
            "3. Clique em **'INCLUIR'** para concluir;\n"
            "4. O sistema gerará automaticamente o **NUP** (Número Único de Protocolo) — guarde este número!\n\n"
            "Se desejar tramitar o documento logo após o cadastro, preencha o campo **'Tramitar Para'** antes de incluir."
        ),
        "confidence": 0.95,
        "page": "Pág. 18-20",
    },
    {
        "source_name": "Manual Módulo Documentos - E-Palmas v1.0",
        "keywords": "tramitar, tramitacao, encaminhar documento, departamento, movimentar",
        "question_hint": "como tramitar documento, como encaminhar para outro departamento, como movimentar protocolo",
        "content": (
            "Para **Tramitar (encaminhar) um Documento** para outro departamento:\n\n"
            "1. Acesse **Módulo Documentos → Listagem**;\n"
            "2. Localize o documento na sua listagem (ele deve estar na situação **'Corrente'**);\n"
            "3. Na barra de ação do documento, clique em **'TRAMITAR'**;\n"
            "4. Selecione o **departamento de destino**;\n"
            "5. Informe o motivo da tramitação (se necessário);\n"
            "6. Confirme a ação.\n\n"
            "**Atenção:**\n"
            "- A tramitação só pode ser cancelada se o departamento de destino **ainda não tiver recebido** o documento;\n"
            "- Para cancelar: acesse **Módulo Documentos → Cancelar Tramitação**;\n"
            "- Para receber: acesse **Módulo Documentos → Receber Tramitação**."
        ),
        "confidence": 0.95,
        "page": "Pág. 90, 111",
    },
    {
        "source_name": "Manual Módulo Documentos - E-Palmas v1.0",
        "keywords": "arquivar, arquivamento, caixa, guarda, desarquivar, situacao arquivado",
        "question_hint": "como arquivar documento, como localizar documento arquivado, como desarquivar",
        "content": (
            "Para **Arquivar um Documento** no E-Palmas:\n\n"
            "1. Acesse **Módulo Documentos → Arquivar**;\n"
            "2. Informe o NUP do documento que deseja arquivar;\n"
            "3. Acione **'PESQUISAR'**;\n"
            "4. Informe a localização física de arquivamento;\n"
            "   - É possível arquivar diretamente em uma **caixa do Módulo Arquivos** (clique em + no campo 'CAIXA');\n"
            "5. Acione o botão **'ARQUIVAR'**.\n\n"
            "**Para acessar um documento arquivado:**\n"
            "Na Listagem, selecione a situação **'ARQUIVADO'** para visualizá-lo.\n\n"
            "**Para Desarquivar:**\n"
            "Localize o documento com situação 'Arquivado' e acione o botão **'DESARQUIVAR'**."
        ),
        "confidence": 0.95,
        "page": "Pág. 8-10",
    },
    {
        "source_name": "Manual Módulo Documentos - E-Palmas v1.0",
        "keywords": "assinatura digital, certificado digital, assinar arquivo, login senha, token",
        "question_hint": "como assinar digitalmente, como usar certificado digital, como fazer assinatura digital no documento",
        "content": (
            "Para **Assinar Digitalmente** um arquivo no E-Palmas:\n\n"
            "1. Acesse **Módulo Documentos → Arquivo Digital**;\n"
            "2. Informe o NUP do documento, pesquise e clique em **'ASSINATURA DIGITAL'**;\n"
            "3. Escolha a forma de assinatura:\n\n"
            "**Opção A — Certificado Digital (token/smart card):**\n"
            "   - Clique em **'ATRAVÉS DE CERTIFICADO DIGITAL'**;\n"
            "   - Selecione o certificado na lista;\n"
            "   - Selecione o arquivo a assinar;\n"
            "   - Clique em **'ASSINAR'** e depois **'FECHAR'**.\n\n"
            "**Opção B — Login e Senha:**\n"
            "   - Clique em **'ATRAVÉS DE LOGIN E SENHA'**;\n"
            "   - O sistema já identificará seu usuário (mesmo login de acesso);\n"
            "   - Digite sua senha;\n"
            "   - Clique em **'ASSINAR'**.\n\n"
            "Após assinar, o documento exibirá um **QR Code** para verificar a autenticidade. ✅"
        ),
        "confidence": 0.95,
        "page": "Pág. 13-16",
    },
    {
        "source_name": "Manual Módulo Documentos - E-Palmas v1.0",
        "keywords": "cancelar documento, reativar, cancelamento nup, desfazer cancelamento",
        "question_hint": "como cancelar documento, como reativar documento cancelado, como desfazer cancelamento",
        "content": (
            "Para **Cancelar um Documento** no E-Palmas:\n\n"
            "1. Acesse **Módulo Documentos → Cancelar/Reativar**;\n"
            "2. Informe o NUP do documento;\n"
            "3. Acione **'PESQUISAR'**;\n"
            "4. Informe o **motivo do cancelamento**;\n"
            "5. Acione **'CANCELAR DOCUMENTO'**.\n\n"
            "**Importante:** O NUP cancelado não desaparece do sistema. Para acessá-lo, "
            "selecione a situação **'CANCELADO'** na Listagem.\n\n"
            "**Para Reativar um Documento Cancelado:**\n"
            "1. Localize o documento com situação 'Cancelado';\n"
            "2. Acione o botão **'RECUPERAR DOCUMENTO'**.\n\n"
            "⚠️ O cancelamento retira a validade probatória do documento."
        ),
        "confidence": 0.95,
        "page": "Pág. 32-35",
    },
    {
        "source_name": "Manual Módulo Documentos - E-Palmas v1.0",
        "keywords": "pesquisa avancada, pesquisa simples, localizar documento, buscar nup, encontrar protocolo",
        "question_hint": "como pesquisar documento, como encontrar protocolo pelo nup, como usar pesquisa avancada",
        "content": (
            "O E-Palmas oferece dois tipos de pesquisa:\n\n"
            "**Pesquisa Simples** (quando você sabe o NUP):\n"
            "1. Acesse **Módulo Documentos → Pesquisa Simples**;\n"
            "2. Digite o número do protocolo (NUP);\n"
            "3. O sistema retornará os dados do documento.\n\n"
            "**Pesquisa Avançada** (quando não sabe o NUP):\n"
            "1. Acesse **Módulo Documentos → Pesquisa Avançada**;\n"
            "2. Preencha os filtros disponíveis:\n"
            "   - Tipo Documental, Data, Assunto, Interessado, Palavras-chave, Departamento, Situação etc.;\n"
            "3. **Quanto mais filtros preenchidos, mais preciso o resultado**;\n"
            "4. Clique em pesquisar.\n\n"
            "💡 **Dica:** Use Palavras-chave cadastradas nos documentos para facilitar buscas futuras."
        ),
        "confidence": 0.95,
        "page": "Pág. 104-106",
    },
    {
        "source_name": "Manual Módulo Documentos - E-Palmas v1.0",
        "keywords": "distribuir documento, distribuicao, funcionario, departamento, receber distribuicao",
        "question_hint": "como distribuir documento para funcionario, como atribuir responsabilidade de documento",
        "content": (
            "Para **Distribuir um Documento** a um funcionário do departamento:\n\n"
            "1. Acesse **Módulo Documentos → Distribuir**;\n"
            "2. Informe o NUP e pesquise;\n"
            "3. Selecione o **funcionário** de destino;\n"
            "4. Informe o **motivo da distribuição** e as **providências** necessárias;\n"
            "5. Indique um **prazo de resposta** (opcional);\n"
            "6. Clique em **'DISTRIBUIR'**.\n\n"
            "**Importante:**\n"
            "- O documento continua na listagem do departamento mesmo após distribuído;\n"
            "- O funcionário recebe o documento e deve usar **Receber Distribuição** para confirmar;\n"
            "- Somente quem distribuiu pode desfazer a distribuição (botão **'DESFAZER'**)."
        ),
        "confidence": 0.95,
        "page": "Pág. 38-40",
    },
    {
        "source_name": "Manual Módulo Documentos - E-Palmas v1.0",
        "keywords": "expedir, expedicao, externo, secretaria, lote, guia expedicao",
        "question_hint": "como expedir documento, como enviar para externo, como fazer expedicao por lote",
        "content": (
            "Para **Expedir um Documento** (enviar para externo ou outra secretaria):\n\n"
            "**Expedição Individual:**\n"
            "1. Acesse **Módulo Documentos → Expedir**;\n"
            "2. Informe o NUP e pesquise;\n"
            "3. Selecione o tipo de expedição:\n"
            "   - **Entre Secretarias**: para departamentos internos;\n"
            "   - **Externa**: para pessoas/instituições externas;\n"
            "4. Preencha os dados do destinatário;\n"
            "5. Confirme.\n\n"
            "**Expedição por Lote** (vários documentos de uma vez):\n"
            "1. Acesse **Módulo Documentos → Expedição por Lote**;\n"
            "2. Selecione os documentos e proceda normalmente.\n\n"
            "Para **desfazer uma expedição**, use a opção **'Desfazer Expedição'** na listagem."
        ),
        "confidence": 0.90,
        "page": "Pág. 44-50",
    },

    # ── MÓDULO PROCESSOS ─────────────────────────────────────────────────────

    {
        "source_name": "Manual Módulo Processos - E-Palmas v1.0",
        "keywords": "processo, formalizar, cadastrar processo, autuacao, nup processo, .0.",
        "question_hint": "como criar processo, como formalizar processo, diferença entre documento e processo no epalmas",
        "content": (
            "No E-Palmas, **Processos** são diferentes de **Documentos**:\n\n"
            "- Documentos são identificados pelo NUP com **.9.** logo antes do número sequencial. Ex: 00000.**9**.000058/2024\n"
            "- Processos são identificados pelo NUP com **.0.** Ex: 00000.**0**.000001/2024\n\n"
            "**Para criar/formalizar um Processo:**\n"
            "1. Acesse **Módulo Processos → Cadastrar**;\n"
            "2. Preencha os campos obrigatórios (marcados com asterisco vermelho);\n"
            "3. O sistema gerará automaticamente o NUP do processo;\n"
            "4. Documentos podem ser juntados ao processo para compor o dossiê.\n\n"
            "**Também é possível formalizar um processo a partir de um documento:**\n"
            "Na Listagem de Documentos, use a opção **'Formalizar Processo Geral'** na barra de ação do documento."
        ),
        "confidence": 0.95,
        "page": "Pág. 1-10",
    },
    {
        "source_name": "Manual Módulo Processos - E-Palmas v1.0",
        "keywords": "alterar processo, alterar documento, corrigir dados, editar cadastro",
        "question_hint": "como alterar dados de um processo, como corrigir informações de um processo",
        "content": (
            "Para **Alterar dados de um Processo** no E-Palmas:\n\n"
            "1. Acesse **Módulo Processos → Listagem**;\n"
            "2. Localize o processo;\n"
            "3. Na barra de ação, clique em **'ALTERAR'**;\n"
            "4. Modifique os campos necessários;\n"
            "5. Clique em **'SALVAR'**.\n\n"
            "**Atenção:** Algumas alterações podem não ser permitidas dependendo do status do processo "
            "(ex: processo em tramitação pode ter restrições de alteração de determinados campos).\n\n"
            "Para documentos, o mesmo processo se aplica via **Módulo Documentos → Listagem → BARRA DE AÇÃO: Alterar**."
        ),
        "confidence": 0.90,
        "page": "Pág. 6-8",
    },

    # ── GLOSSÁRIO ────────────────────────────────────────────────────────────

    {
        "source_name": "Glossário SIGED - E-Palmas",
        "keywords": "nup, numero unico protocolo, o que e nup, significado nup",
        "question_hint": "o que é NUP, o que significa NUP, para que serve o número de protocolo",
        "content": (
            "**NUP — Número Único de Protocolo**\n\n"
            "O NUP é um conjunto numérico sequencial e único atribuído automaticamente pelo sistema E-Palmas a cada "
            "documento ou processo cadastrado. Ele fornece informações sobre:\n"
            "- A **origem** do protocolo (departamento/secretaria);\n"
            "- O **tipo** (documento .9. ou processo .0.);\n"
            "- O **número sequencial** e o **ano** de produção.\n\n"
            "**Exemplo:** 00000.9.000058/2024 (documento) ou 00000.0.000001/2024 (processo)\n\n"
            "O NUP é o principal identificador para realizar qualquer ação no sistema: tramitar, arquivar, "
            "pesquisar, expedir, assinar, etc. **Guarde sempre o NUP após cadastrar um documento!**"
        ),
        "confidence": 0.98,
        "page": "Glossário, pág. 5",
    },
    {
        "source_name": "Glossário SIGED - E-Palmas",
        "keywords": "arquivar, corrente, situacao, status documento",
        "question_hint": "quais são as situações de um documento no epalmas, o que significa corrente arquivado sobrestado",
        "content": (
            "**Situações de um documento/protocolo no E-Palmas:**\n\n"
            "| Situação | Significado |\n"
            "|---|---|\n"
            "| **Corrente** | Documento em tramitação, uso ativo |\n"
            "| **Arquivado** | Arquivado virtualmente no sistema (ainda acessível) |\n"
            "| **Sobrestado** | Suspenso temporariamente aguardando providência |\n"
            "| **Expedido** | Enviado para destinatário externo |\n"
            "| **Cancelado** | Cancelado (sem validade, mas não apagado) |\n"
            "| **Tramitando** | Em movimento entre departamentos |\n\n"
            "Para filtrar por situação, use a **Listagem** e selecione a situação desejada no filtro."
        ),
        "confidence": 0.98,
        "page": "Glossário, pág. 3-5",
    },
    {
        "source_name": "Glossário SIGED - E-Palmas",
        "keywords": "perfil usuario, administrador, tecnico, protocolo, permissoes, acesso sistema",
        "question_hint": "quais são os perfis de usuario no epalmas, não consigo acessar funcionalidade, sem permissão",
        "content": (
            "**Perfis de usuário no E-Palmas (SIGED):**\n\n"
            "O acesso às funcionalidades é controlado pelo **perfil** atribuído ao usuário:\n\n"
            "- **Administrador**: acesso completo ao sistema, inclui configurações e manutenções;\n"
            "- **Técnico/Analista**: acesso a funcionalidades operacionais do módulo;\n"
            "- **Protocolo**: atendimento em guichê, pré-cadastro e cadastro de documentos externos;\n"
            "- **Usuário externo**: acesso ao portal para protocolar documentos.\n\n"
            "Se você não consegue acessar uma funcionalidade, verifique:\n"
            "1. Se o seu perfil tem permissão para essa ação;\n"
            "2. Se o documento/processo está na **carga do seu departamento**;\n"
            "3. Se a situação do documento permite a ação (ex: documento expedido não pode ser tramitado).\n\n"
            "Para solicitar ajuste de perfil/permissão, entre em contato com o **administrador do sistema** da sua instituição."
        ),
        "confidence": 0.95,
        "page": "Glossário, pág. 6",
    },
    {
        "source_name": "Glossário SIGED - E-Palmas",
        "keywords": "sobrestar, sobrestamento, suspender, aguardando providencia",
        "question_hint": "o que é sobrestar, como sobrestar um documento, diferença entre sobrestar e arquivar",
        "content": (
            "**Sobrestar** é uma ação que coloca o documento em **fase de suspensão temporária**.\n\n"
            "Diferente do arquivamento, o sobrestamento indica que o documento está aguardando uma providência para "
            "continuar tramitando (ex: envio de outros documentos, decisão, pesquisa, prazo).\n\n"
            "**Diferença Sobrestar × Arquivar:**\n"
            "- **Sobrestar**: suspensão temporária de ações, aguardando retomada;\n"
            "- **Arquivar**: guarda definitiva (pode estar finda a tramitação).\n\n"
            "Para sobrestar: **Listagem → Barra de Ação → SOBRESTAR**.\n"
            "Para reativar um documento sobrestado: use **TRAMITAR** ou outra ação disponível."
        ),
        "confidence": 0.90,
        "page": "Glossário, pág. 6",
    },
]


def ingest_chunks():
    print("=== Ingestão de Knowledge Chunks ===\n")

    # Remove chunks de PDF antigos (para re-ingestão limpa)
    old = KnowledgeChunk.objects.filter(
        source_type__in=[KnowledgeChunk.SourceType.PDF_MANUAL, KnowledgeChunk.SourceType.FAQ]
    )
    count_old = old.count()
    if count_old > 0:
        old.delete()
        print(f"Removidos {count_old} chunks antigos de PDF/FAQ.\n")

    created = 0
    for chunk_data in MANUAL_CHUNKS:
        KnowledgeChunk.objects.create(
            source_type=KnowledgeChunk.SourceType.PDF_MANUAL,
            source_name=chunk_data["source_name"],
            keywords=chunk_data["keywords"],
            question_hint=chunk_data["question_hint"],
            content=chunk_data["content"],
            confidence_score=chunk_data["confidence"],
            page_reference=chunk_data.get("page", ""),
        )
        print(f"  [OK] {chunk_data['source_name'][:50]} | {chunk_data['question_hint'][:60]}")
        created += 1

    print(f"\nTotal: {created} chunks criados no banco.\n")

    # Verifica
    total = KnowledgeChunk.objects.filter(is_active=True).count()
    print(f"Total de chunks ativos no banco: {total}")
    print("\nIngestão concluída com sucesso!")


if __name__ == "__main__":
    ingest_chunks()
