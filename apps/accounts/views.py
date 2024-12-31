from apps.accounts.serializers import (UserDetailsSerializer, UserAddSerializer, MyTokenObtainPairSerializer, UpdateUserDetailsByAdminSerializer,PasswordResetSerializer)
from rest_framework.permissions import AllowAny, IsAuthenticated
from apps.accounts.mixins import CustomAuthenticationMixin
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework import mixins, viewsets
from rest_framework.views import APIView
from apps.accounts.models import User
from django.utils import timezone
from django.conf import settings


class Test(APIView):
    def post(self, request):
        return Response({"detail":"this is working"})

class RegisterAdmin(viewsets.GenericViewSet, mixins.CreateModelMixin):
    serializer_class = UserAddSerializer
    permission_classes = (AllowAny,)
    queryset = get_user_model().objects.all()

class LoginUser(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            # Token.objects.filter(user=user).delete()    
            token, _ = Token.objects.get_or_create(user=user)
            user_data = UserDetailsSerializer(user).data
            response_data = {"token": {"access": token.key,},**user_data}
            user.last_login = timezone.now()
            user.save()
            return Response(response_data, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.user.auth_token.delete()
        return Response({"message": "User logged out"}, status=200)


class CreateUserByAdmin(mixins.CreateModelMixin, CustomAuthenticationMixin, viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = UserAddSerializer

    def check_permissions(self, request):
        self.validate_user_type(request, allowed=['Admin'])
        return super().check_permissions(request)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['created_by'] = self.request.user
        context['updated_by'] = self.request.user
        return context


class GetAllUsersByAdmin(mixins.ListModelMixin, viewsets.GenericViewSet, CustomAuthenticationMixin):
    permission_classes = [IsAuthenticated]
    queryset = User.objects
    serializer_class = UserDetailsSerializer

    def check_permissions(self, request):
        self.validate_user_type(request=request, allowed=['Admin', 'Receptionist'])
        return super().check_permissions(request)

    def get_queryset(self):
        data = super().get_queryset()
        data = data.filter(is_active=True).order_by("-updated_on")
        return data


class UpdateUserDetailsByAdmin(generics.UpdateAPIView, CustomAuthenticationMixin):
    permission_classes = [IsAuthenticated]
    serializer_class = UpdateUserDetailsByAdminSerializer
    queryset = User.objects
    lookup_field = 'id'

    def check_permissions(self, request):
        self.validate_user_type(request, allowed=['Admin'])
        return super().check_permissions(request)


class ResetPasswordByUser(generics.UpdateAPIView, CustomAuthenticationMixin):
    permission_classes = [IsAuthenticated]
    serializer_class = PasswordResetSerializer

    def get_object(self):
        usr = self.request.user
        return usr


class ResetPasswordByAdmin(generics.UpdateAPIView, CustomAuthenticationMixin):
    permission_classes = [IsAuthenticated]
    serializer_class = PasswordResetSerializer
    queryset = User.objects
    lookup_field = 'id'

    def check_permissions(self, request):
        self.validate_user_type(request, allowed=['Admin'])
        return super().check_permissions(request)


class ValidateTokenAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        try:
            token_key = request.data.get('token')
            if not token_key:
                return Response({'error': 'Token is required'}, status=400)
            
            # Validate token existence and retrieve the associated user
            token = Token.objects.filter(key=token_key).first()
            if not token:
                return Response({'valid': False, 'message': 'Invalid token'}, status=400)

            return Response({'valid': True, 'user_id': token.user.id}, status=200)
        except Exception as e:
            return Response({'detail': str(e)}, status=400)
