import jwt
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from datetime import datetime, timedelta
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
import os
from rest_framework import status
from dotenv import load_dotenv
from rest_framework_simplejwt.backends import TokenBackend
from rest_framework.exceptions import PermissionDenied

class TokenService:
    invalidated_tokens = {}
    token_class = RefreshToken

    @classmethod
    def get_token_for_user(cls, user):
        
        refresh = cls.token_class.for_user(user)
        refresh['username'] = user.username
        refresh['user_type'] = user.user_type
        return {
            'refresh_token': str(refresh),
            'access_token': str(refresh.access_token),
        }

    @staticmethod
    def decode_token(token):
        if token is None:
            return {}
        
        token_backend = TokenBackend(algorithm='HS256', signing_key=os.environ.get('SECRET_KEY'))
        validated_token = token_backend.decode(token.strip())
        return validated_token

    @staticmethod
    def get_tokens_for_user(user):
        # Not to be used anymore
        if user is None:
            return {'error': 'No user is provided'}

        secret_key = os.getenv('SECRET_KEY')
        algorithm = os.getenv('ALGORITHM')

        access_token_expiration = datetime.utcnow() + timedelta(minutes=int(os.getenv('ACCESS_TOKEN_EXPIRY')))
        

        access_payload = {
            'user_id': user.id,
            'exp': access_token_expiration,
            'user_type': user.user_type,
            'user_name': user.user_name
        }
        access_token = jwt.encode(access_payload, secret_key, algorithm)

        

        return access_token
            
    @staticmethod
    def verify_token(token):
        # Not to be used anymore
        if token is None:
            return {"valid": False, "error": "No token provided"}

        if token in TokenService.invalidated_tokens:
            return {"valid": False, "error": "Token has been invalidated"}

        secret_key = os.getenv('SECRET_KEY')
        algorithm = os.getenv('ALGORITHM')

        try:
            valid_data = jwt.decode(token, secret_key, algorithms=[algorithm])

            user_type = valid_data.get('user_type', 'Unknown')
            user_name = valid_data.get('user_name', 'Unknown')
            user_id = valid_data.get('user_id', 'Unknown')
            return {"valid": True, "user_type": user_type, "user_name": user_name, "user_id": user_id, "payload": valid_data}
        except ExpiredSignatureError:
            return {"valid": False, "error": "Token has expired"}
        except InvalidTokenError:
            return {"valid": False, "error": "Invalid token"}

    @staticmethod
    def invalidate_token(token):
        # Not to be used anymore
        try:
            secret_key = os.getenv('SECRET_KEY')

            payload = jwt.decode(token, options={"verify_signature": False})
            exp_time = datetime.utcfromtimestamp(payload['exp'])

            TokenService.invalidated_tokens[token] = exp_time
            return {"valid": True, "message": "Token invalidated"}
        except (ExpiredSignatureError, InvalidTokenError):
            return {"valid": False, "error": "Invalid token, cannot invalidate"}


def validation(request, allowed):
    token = request.headers.get('Authorization')
    # token_verification = TokenService.verify_token(token)
    token_data = TokenService.decode_token(token)
    if token_data['user_type'] in allowed:
        return True
    raise PermissionDenied()
