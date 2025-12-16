from rest_framework import permissions

class IsFarmer(permissions.BasePermission):
    """
    Allow access only to authenticated users with role 'farmer'.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and getattr(request.user, 'role', None) == 'farmer')

class IsAdmin(permissions.BasePermission):
    """
    Allow access only to authenticated users with role 'admin'.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and getattr(request.user, 'role', None) == 'admin')

class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object or admins to access it.
    Assumes the model instance has an `owner` attribute (e.g. ForeignKey to CustomUser).
    """
    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        if getattr(request.user, 'role', None) == 'admin':
            return True
        # fallback: compare owner attribute (adapt if your models use a different field name)
        owner = getattr(obj, 'owner', None)
        return owner == request.user
