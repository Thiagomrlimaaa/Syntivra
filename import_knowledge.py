import os, django, sys

# Configurar ambiente Django
sys.path.append(os.path.join(os.getcwd(), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.tickets.models import Ticket
from apps.tenants.models import Organization
from apps.users.models import User

def import_tickets(data):
    """
    Importa tickets reais para a base de conhecimento (Aprendizado da IA).
    Formato esperado de data:
    [
        {"title": "Erro ao imprimir boleto", "description": "O cliente relatou erro de timeout no PDF.", "solution": "Reiniciamos o pool e limpamos cache."},
        ...
    ]
    """
    org = Organization.objects.first()
    admin = User.objects.filter(role='ADMIN').first()

    if not org or not admin:
        print("Erro: Nenhuma organização ou admin encontrado.")
        return

    count = 0
    for item in data:
        # Criamos o ticket já como RESOLVIDO para entrar na base de sugestões
        t = Ticket.objects.create(
            organization=org,
            created_by=admin,
            title=item['title'],
            description=item['description'],
            status='RESOLVED' # Essencial para que a IA o encontre
        )
        count += 1
    
    print(f"Sucesso! {count} chamados reais absorvidos pela inteligência da plataforma.")

if __name__ == "__main__":
    # Exemplo de chamados reais para você carregar
    # Substitua pelos dados da sua empresa:
    meus_dados_reais = [
        {
            "title": "Ajuste na integração com API do PagSeguro", 
            "description": "O cliente não conseguia finalizar a compra pois o token estava expirado.", 
            "solution": "Redefinimos o token no painel e atualizamos as variáveis de ambiente."
        },
        {
            "title": "Configuração de roteador Mikrotik para porta 8080", 
            "description": "Porta estava bloqueada pelo firewall interno.", 
            "solution": "Adicionada regra de NAT permitindo tráfego na chain dst-nat."
        },
        {
            "title": "Lentidão recorrente no banco de dados", 
            "description": "A carga de trabalho excedeu a memória disponível.", 
            "solution": "Realizamos o upgrade de instância para 16GB e otimizamos os índices da tabela de logs."
        }
    ]

    import_tickets(meus_dados_reais)
