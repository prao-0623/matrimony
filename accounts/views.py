from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.middleware.csrf import get_token
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from .models import StaffStatus
from .permissions import IsAdminOrSuperAdmin, IsSuperAdmin
from .serializers import StaffAdminCreateSerializer, StaffUserSerializer

User = get_user_model()


def _get_auth_response(user):
    refresh = RefreshToken.for_user(user)
    serializer = StaffUserSerializer(user)
    return {
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'user': serializer.data,
    }


def _set_browser_tokens(response, access_token=None, refresh_token=None):
    if access_token:
        response.set_cookie(
            'access_token',
            access_token,
            httponly=True,
            secure=not settings.DEBUG,
            samesite='Lax',
            max_age=15 * 60,
            path='/',
        )
    if refresh_token:
        response.set_cookie(
            'refresh_token',
            refresh_token,
            httponly=True,
            secure=not settings.DEBUG,
            samesite='Lax',
            max_age=7 * 24 * 60 * 60,
            path='/',
        )
    return response


def _clear_browser_tokens(response):
    response.delete_cookie('access_token', path='/', samesite='Lax')
    response.delete_cookie('refresh_token', path='/', samesite='Lax')
    return response


class CsrfCookieView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        get_token(request)
        return Response({'detail': 'CSRF cookie set.'}, status=status.HTTP_200_OK)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({'detail': 'Email and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, email=email, password=password)
        if user is None or not user.is_active or user.status != StaffStatus.ACTIVE:
            return Response({'detail': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)

        tokens = _get_auth_response(user)
        return Response({
            'access': tokens['access'],
            'refresh': tokens['refresh'],
            'user': tokens['user'],
        }, status=status.HTTP_200_OK)


class BrowserLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({'detail': 'Email and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, email=email, password=password)
        if user is None or not user.is_active or user.status != StaffStatus.ACTIVE:
            return Response({'detail': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)

        tokens = _get_auth_response(user)
        response = Response({'detail': 'Logged in successfully.', 'user': tokens['user']}, status=status.HTTP_200_OK)
        return _set_browser_tokens(response, tokens['access'], tokens['refresh'])


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({'refresh': 'This field is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            refresh = RefreshToken(refresh_token)
            if str(refresh['user_id']) != str(request.user.pk):
                return Response({'detail': 'Invalid refresh token.'}, status=status.HTTP_400_BAD_REQUEST)
            refresh.blacklist()
        except TokenError:
            return Response({'detail': 'Invalid or expired refresh token.'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'detail': 'Logged out successfully.'}, status=status.HTTP_205_RESET_CONTENT)


class BrowserLogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.COOKIES.get('refresh_token') or request.data.get('refresh')
        if not refresh_token:
            return Response({'detail': 'Refresh token is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            refresh = RefreshToken(refresh_token)
            if str(refresh['user_id']) != str(request.user.pk):
                return Response({'detail': 'Invalid refresh token.'}, status=status.HTTP_400_BAD_REQUEST)
            refresh.blacklist()
        except TokenError:
            return Response({'detail': 'Invalid or expired refresh token.'}, status=status.HTTP_400_BAD_REQUEST)

        response = Response({'detail': 'Logged out successfully.'}, status=status.HTTP_205_RESET_CONTENT)
        return _clear_browser_tokens(response)


class BrowserRefreshView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.COOKIES.get('refresh_token')
        if not refresh_token:
            return Response({'detail': 'Refresh token is required.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = TokenRefreshSerializer(data={'refresh': refresh_token})
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as exc:
            raise InvalidToken(str(exc))

        validated = serializer.validated_data
        response = Response({
            'access': validated['access'],
            'refresh': validated.get('refresh', refresh_token),
        }, status=status.HTTP_200_OK)
        return _set_browser_tokens(response, validated['access'], validated.get('refresh', refresh_token))


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = StaffUserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class StaffAdminListCreateAPIView(generics.ListCreateAPIView):
    queryset = User.objects.all().order_by('-created_at')
    serializer_class = StaffUserSerializer
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return StaffAdminCreateSerializer
        return StaffUserSerializer

    def get_queryset(self):
        return User.objects.all().order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        user.created_by = request.user
        user.save()
        response_serializer = StaffUserSerializer(user)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
