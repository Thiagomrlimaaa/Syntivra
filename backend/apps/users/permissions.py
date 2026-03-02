from rest_framework import permissions

class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'ADMIN'

class IsTechnicianUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['ADMIN', 'TECHNICIAN']

class IsTenantOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Assumes obj has an 'organization' field or is an Organization
        if hasattr(obj, 'organization'):
            return obj.organization_id == request.user.organization_id
        return obj.id == request.user.organization_id
