import contextvars

_tenant_id = contextvars.ContextVar("tenant_id", default=None)

def set_current_tenant_id(tenant_id):
    _tenant_id.set(tenant_id)

def get_current_tenant_id():
    return _tenant_id.get()
