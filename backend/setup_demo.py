"""
Script de setup completo dos dados de demo do Syntivra.
Recria os usuários admin e cliente com senhas conhecidas e organização configurada.
"""
import os, sys, django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, '.')
django.setup()

from apps.tenants.models import Organization
from django.contrib.auth import get_user_model

User = get_user_model()

print("=== Setup de dados de demo ===\n")

# 1. Cria/garante a organização de demo
org, created = Organization.objects.get_or_create(
    slug='demo',
    defaults={'name': 'Empresa Demo'}
)
action = "Criada" if created else "Encontrada"
print(f"{action} organizacao: {org.name} (id={org.id})")

# 2. Admin
admin, created = User.objects.get_or_create(
    cpf='00000000000',
    defaults={
        'email': 'admin@demo.com',
        'first_name': 'Admin',
        'last_name': 'Syntivra',
        'role': 'ADMIN',
        'is_staff': True,
        'is_superuser': True,
        'organization': org,
        'is_active': True,
    }
)
admin.set_password('admin123')
admin.organization = org
admin.role = 'ADMIN'
admin.is_staff = True
admin.is_superuser = True
admin.is_active = True
admin.save()
action = "Criado" if created else "Atualizado"
print(f"{action} admin: CPF=000.000.000-00  email=admin@demo.com  senha=admin123  org={org.name}")

# 3. Cliente
cliente, created = User.objects.get_or_create(
    cpf='11111111111',
    defaults={
        'email': 'cliente@demo.com',
        'first_name': 'Cliente',
        'last_name': 'Demo',
        'role': 'CUSTOMER',
        'organization': org,
        'is_active': True,
    }
)
cliente.set_password('cliente123')
cliente.organization = org
cliente.role = 'CUSTOMER'
cliente.is_active = True
cliente.save()
action = "Criado" if created else "Atualizado"
print(f"{action} cliente: CPF=111.111.111-11  email=cliente@demo.com  senha=cliente123  org={org.name}")

# 4. Verificacao final
print("\n=== Verificacao de autenticacao ===")
from django.contrib.auth import authenticate

for cpf, pw, label in [('00000000000', 'admin123', 'Admin'), ('11111111111', 'cliente123', 'Cliente')]:
    u = authenticate(cpf=cpf, password=pw)
    if u:
        print(f"  OK  {label} (CPF={cpf}) autenticado -> role={u.role} org={u.organization}")
    else:
        print(f"  ERRO {label} (CPF={cpf}) - autenticacao falhou!")

print("\nSetup concluido.")
