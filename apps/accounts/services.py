from rest_framework.authtoken.models import Token

class TokenService:
    @staticmethod
    def get_or_create_token(user):
        token, created = Token.objects.get_or_create(user=user)
        return token.key

    @staticmethod
    def delete_token(user):
        Token.objects.filter(user=user).delete()
