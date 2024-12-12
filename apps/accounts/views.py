from apps.accounts.serializers import (UserDetailsSerializer, UserAddSerializer, MyTokenObtainPairSerializer, UpdateUserDetailsByAdminSerializer,PasswordResetSerializer)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from apps.accounts.mixins import CustomAuthenticationMixin
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework import mixins, viewsets
from rest_framework.views import APIView
from apps.accounts.models import User
from django.conf import settings
import jwt



class Test(APIView):
    def post(self, request):
        return Response({"message":"this is working"})

class RegisterAdmin(viewsets.GenericViewSet, mixins.CreateModelMixin):
    
    serializer_class = UserAddSerializer
    permission_classes = (AllowAny,)
    queryset = get_user_model().objects.all()

class LoginUser(TokenObtainPairView):
    permission_classes = (AllowAny,)
    serializer_class = MyTokenObtainPairSerializer

class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            # session = UserSession.objects.filter(user_id=request.user.id, logout_time__isnull=True).latest('login_time')
            # session.logout_time = timezone.now()
            # session.save()
            token.blacklist()

            return Response({"message": "User logged out"}, status=200)
        except Exception as e:
            return Response({"message":"something went wrong"},status=400)
        
class CreateUserByAdmin(mixins.CreateModelMixin, CustomAuthenticationMixin, viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated,]
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

    permission_classes = [IsAuthenticated,]
    queryset = User.objects
    serializer_class = UserDetailsSerializer
    
    def check_permissions(self, request):
        self.validate_user_type(request=request, allowed=['Admin','Receptionist'])
        return super().check_permissions(request)
     
    def get_queryset(self):
        data = super().get_queryset()
        data = data.filter(is_active = True).order_by("-updated_on")
        return data
    
class UpdateUserDetailsByAdmin(generics.UpdateAPIView, CustomAuthenticationMixin):

    permission_classes = [IsAuthenticated,]
    serializer_class = UpdateUserDetailsByAdminSerializer
    queryset = User.objects
    lookup_field = 'id'

    def check_permissions(self, request):
        self.validate_user_type(request, allowed=['Admin'])
        return super().check_permissions(request)

class ResetPasswordByUser(generics.UpdateAPIView, CustomAuthenticationMixin):
    
    permission_classes = [IsAuthenticated,]
    serializer_class = PasswordResetSerializer

    def get_object(self):
        usr = self.request.user
        return usr
    
class ResetPasswordByAdmin(generics.UpdateAPIView, CustomAuthenticationMixin):
    permission_classes = [IsAuthenticated,]
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
            token = request.data.get('token')
            if not token:
                return Response({'error': 'Token is required'}, status=400)
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            return Response({'valid': True, 'payload': payload})
        except jwt.ExpiredSignatureError:
            return Response({'valid': False, 'message': 'Token has expired'})
        except jwt.InvalidTokenError:
            return Response({'valid': False, 'message': 'Invalid token'})
        except Exception as e :
            return Response({"detail":str(e)})
