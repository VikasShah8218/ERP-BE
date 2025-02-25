from rest_framework.permissions import BasePermission

class HasCustomPermission(BasePermission):
    def has_permission(self, request, view):
        required_perm = getattr(view, "required_permission", None)  # Get permission from view
        return required_perm is None or request.user.has_custom_permission(required_perm)


# class HasCustomPermission(BasePermission):
#     def has_permission(self, request, view):
#         required_perm = getattr(view, "required_permission", None)  # Get permission from ViewSet
#         if required_perm is None:
#             return True  # Allow access if no specific permission is required
#         # return request.user.has_custom_permission(required_perm)  # Check user permissions
#         return request.user.permissions.filter(codename=required_perm).exists()