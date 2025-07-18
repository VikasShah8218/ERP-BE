from typing import Any, Dict
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.utils import timezone
from rest_framework.authtoken.models import Token
from .models import Department



class UserDetailsSerializer(serializers.ModelSerializer):
    permissions = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        exclude = ('password',)

    def get_permissions(self, obj): return list(obj.permissions.values_list("codename", flat=True))


class DepartmentGETSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department()
        fields = '__all__'



class MyTokenObtainPairSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        token = super(MyTokenObtainPairSerializer, cls).get_token(user)

        # Add custom claims
        token['username'] = user.username
        token['user_type'] = user.user_type
        return token

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, str]:
        validated_data = super().validate(attrs)
        validated_data['token'] = dict()
        validated_data['token'].update({
            'access': validated_data.pop('access'),
            'refresh': validated_data.pop('refresh'),
        })
        self.user.last_login = timezone.now()
        self.user.save()
        validated_data.update(**UserDetailsSerializer(self.user).data)
        return validated_data

class UserAddSerializer(serializers.ModelSerializer):
    token = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = '__all__'
        extra_kwargs = {
            'password': {
                'write_only': True,
                'min_length': 5,
            },
            'first_name': {'required': True},
            'last_name': {'required': True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password')
        if self.context.get('created_by'):
            validated_data['created_by'] = self.context['created_by']
            validated_data['updated_by'] = self.context['updated_by']
        user = get_user_model().objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def get_token(self, user):
        token, _ = Token.objects.get_or_create(user=user)
        return token.key

class UpdateUserDetailsByAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = '__all__'
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'password': {
                'required': False,
                'write_only': True,
                'min_length': 4,
            },
        }

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)

        for (key, value) in validated_data.items():
            setattr(instance, key, value)

        if password is not None:
            instance.set_password(password)

        instance.save()
        return instance

class PasswordResetSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('password',)
        extra_kwargs = {
            'password': {'write_only': True},
        }
    
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)

        if password is not None:
            instance.set_password(password)

        instance.save()
        return instance

class UserAddSerializer(serializers.ModelSerializer):
    token = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = '__all__'
        extra_kwargs = {
            'password': {
                'write_only': True,
                'min_length': 4,
            },
            'first_name': {'required': True},
            'last_name': {'required': True}
        }

    def create(self, validated_data):
        print("\n",validated_data,"\n")
        password = validated_data.pop('password')
        # validated_data.pop('groups')
        # validated_data.pop('user_permissions')
        if self.context.get('created_by'):
            validated_data['created_by'] = self.context['created_by']
            validated_data['updated_by'] = self.context['updated_by']
        user = get_user_model().objects.create(**validated_data)
        user.set_password(password)
        user.is_active = True
        user.save()
        return user

    def get_token(self, user):
        token, _ = Token.objects.get_or_create(user=user)
        return token.key



