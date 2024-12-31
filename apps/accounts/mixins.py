from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import PermissionDenied
from rest_framework.authtoken.models import Token

class CustomAuthenticationMixin(object):
    def validate_user_type(self, request, allowed: list):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith("Token "):
            raise PermissionDenied({'detail': 'Authentication token not provided or invalid'})
        token = auth_header.split()[1]
        user = Token.objects.get(key=token).user
        if user.user_type in allowed:
            return True
        raise PermissionDenied({'detail': f'User type: {user.user_type} not authorized'})
