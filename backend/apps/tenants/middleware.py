from .utils import set_current_tenant_id


class TenantMiddleware:
    """
    Middleware de isolamento multi-tenant.

    IMPORTANTE: Com JWT Bearer token, o request.user no middleware Django
    é sempre AnonymousUser — a autenticação DRF só acontece dentro das views.
    Por isso, decodificamos o token manualmente aqui para extrair o tenant.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        set_current_tenant_id(None)

        tenant_id = self._resolve_tenant(request)
        if tenant_id:
            set_current_tenant_id(tenant_id)

        response = self.get_response(request)

        # Limpa após a resposta para evitar vazamento entre threads
        set_current_tenant_id(None)
        return response

    def _resolve_tenant(self, request):
        """
        Tenta extrair o organization_id em duas estratégias:
        1. request.user já autenticado (sessão Django admin, testes, etc.)
        2. Decodificação direta do Bearer token JWT (caso mais comum no SaaS)
        """
        # Estratégia 1: usuário já autenticado pelo Django (ex: admin panel)
        if hasattr(request, 'user') and request.user.is_authenticated:
            org_id = getattr(request.user, 'organization_id', None)
            if org_id:
                return org_id

        # Estratégia 2: Bearer token JWT no header Authorization
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header.startswith('Bearer '):
            return None

        token = auth_header.split(' ', 1)[1]
        try:
            from rest_framework_simplejwt.tokens import UntypedToken
            from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
            from django.contrib.auth import get_user_model

            # Valida e decodifica o token (lança exceção se inválido/expirado)
            UntypedToken(token)

            import jwt
            from django.conf import settings
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=['HS256'],
                options={'verify_exp': True}
            )

            user_id = payload.get('user_id')
            if not user_id:
                return None

            User = get_user_model()
            user = User.objects.select_related('organization').filter(pk=user_id).first()
            if user and user.organization_id:
                return user.organization_id

        except Exception:
            # Token inválido, expirado, ou usuário não encontrado — sem tenant
            pass

        return None
