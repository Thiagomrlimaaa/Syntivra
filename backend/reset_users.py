import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.users.models import User
from apps.tenants.models import Organization

User.objects.all().delete()
org, _ = Organization.objects.get_or_create(name='Empresa Demo')

User.objects.create_superuser(
    cpf='00000000000', 
    email='admin@demo.com', 
    password='admin123', 
    first_name='Thiago', 
    organization=org
)

User.objects.create_user(
    cpf='11111111111', 
    email='cliente@demo.com', 
    password='cliente123', 
    first_name='Ricardo', 
    role='CUSTOMER', 
    organization=org
)

print('--- Usuarios Resetados: Thiago (Admin) e Ricardo (Cliente) ---')
