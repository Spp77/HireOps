from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.contrib.auth import get_user_model
from .serializers import RegisterSerializer, UserSerializer
from apps.common.exceptions import error_response
from apps.common.error_codes import ErrorCode
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()

            # Fire welcome email asynchronously (non-blocking)
            from apps.accounts.tasks import send_welcome_email
            send_welcome_email.delay(user.pkid)

            logger.info('New user registered', extra={'user_id': str(user.id), 'role': user.role})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return error_response(ErrorCode.REGISTER_FAILED, str(e))


class MeView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        try:
            kwargs['partial'] = True
            return super().update(request, *args, **kwargs)
        except Exception as e:
            return error_response(ErrorCode.PROFILE_UPDATE_FAILED, str(e))


class LogoutView(APIView):
    """
    POST /auth/logout/
    Body: { "refresh": "<refresh_token>" }
    Blacklists the refresh token — stateless JWT invalidation.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return error_response(ErrorCode.VALIDATION_ERROR, 'Refresh token is required.')
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            logger.info('User logged out', extra={'user_id': str(request.user.id)})
            return Response({'detail': 'Successfully logged out.'}, status=status.HTTP_205_RESET_CONTENT)
        except TokenError as e:
            return error_response(ErrorCode.VALIDATION_ERROR, str(e))
