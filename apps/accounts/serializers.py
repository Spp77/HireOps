from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from apps.common.error_codes import ErrorCode

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'first_name', 'last_name', 'role', 'password']
        read_only_fields = ['id']

    def create(self, validated_data):
        try:
            password = validated_data.pop('password')
            user = User(**validated_data)
            user.set_password(password)
            user.save()
            return user
        except IntegrityError:
            raise serializers.ValidationError({
                'code':   ErrorCode.USER_ALREADY_EXISTS,
                'detail': 'User with this email or username already exists.',
            })
        except Exception as e:
            raise serializers.ValidationError({'code': ErrorCode.REGISTER_FAILED, 'detail': str(e)})


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'first_name', 'last_name', 'role']
        read_only_fields = ['id', 'email', 'role']


class CustomTokenObtainSerializer(TokenObtainPairSerializer):
    """
    Extends the default login response to include user info
    alongside the tokens — saves the frontend a round-trip.

    Response:
      {
        "access":     "...",
        "refresh":    "...",
        "user": {
          "id": "...",  "email": "...",
          "role": "CANDIDATE",  "full_name": "Alice Smith"
        }
      }
    """

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Embed lightweight claims in the token itself
        token['role']  = user.role
        token['email'] = user.email
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = {
            'id':        str(self.user.id),
            'email':     self.user.email,
            'role':      self.user.role,
            'full_name': self.user.get_full_name(),
        }
        return data
