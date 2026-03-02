import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, '.')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

# Redefine senha do admin
admin = User.objects.filter(cpf='00000000000').first()
if admin:
    admin.set_password('admin123')
    admin.save()
    print(f"✅ Admin (CPF: 000.000.000-00) -> senha: admin123")

# Redefine senha do cliente
cliente = User.objects.filter(cpf='11111111111').first()
if cliente:
    cliente.set_password('cliente123')
    cliente.save()
    print(f"✅ Cliente (CPF: 111.111.111-11) -> senha: cliente123")

print("\nCredenciais prontas para uso.")
