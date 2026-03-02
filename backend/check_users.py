import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, '.')
django.setup()
from django.contrib.auth import get_user_model
User = get_user_model()

lines = []
lines.append(f"Total de usuarios: {User.objects.count()}")
for u in User.objects.all():
    lines.append(f"CPF={u.cpf!r}  email={u.email!r}  role={u.role}  active={u.is_active}  staff={u.is_staff}  superuser={u.is_superuser}")

with open("users_report.txt", "w") as f:
    f.write("\n".join(lines))

print("Done - wrote users_report.txt")
