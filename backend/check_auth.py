import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, '.')
django.setup()

from django.contrib.auth import get_user_model, authenticate
User = get_user_model()

# Lista todos os usuários
print("=== Usuarios no banco ===")
for u in User.objects.all():
    print(f"  CPF={u.cpf!r}  email={u.email!r}  role={u.role}  active={u.is_active}  has_usable_pw={u.has_usable_password()}")

print()

# Testa autenticacao direta
print("=== Teste de autenticacao ===")
test_cases = [
    ('00000000000', 'admin123'),
    ('11111111111', 'cliente123'),
]

for cpf, pw in test_cases:
    user = authenticate(cpf=cpf, password=pw)
    if user:
        print(f"  OK - CPF={cpf} autenticado -> role={user.role}")
    else:
        print(f"  FALHOU - CPF={cpf} com senha '{pw}'")
        try:
            u = User.objects.get(cpf=cpf)
            ok = u.check_password(pw)
            print(f"     check_password('{pw}') = {ok}")
        except User.DoesNotExist:
            print(f"     Usuario NAO existe no banco!")
