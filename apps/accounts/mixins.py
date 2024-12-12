from rest_framework.exceptions import PermissionDenied

from apps.accounts.services import TokenService

class CustomAuthenticationMixin(object):

    """
    Use this to validate user by the User - role. 
    You can add custom validations and use it in your project
    """

    def validate_user_type(self, request, allowed: list):
        jwt_token = request.headers.get('Authorization')
        if not jwt_token or not len(jwt_token.split())==2:
            raise PermissionDenied({'detail': 'Authentication token not provided'})
        token_data = TokenService.decode_token(jwt_token.split()[1])
        if token_data['user_type'] in allowed:
            return True
        raise PermissionDenied({'detail': f'User type: {token_data['user_type']} Not Authorized'})

