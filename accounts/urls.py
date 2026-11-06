from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    BrowserLoginView,
    BrowserLogoutView,
    BrowserRefreshView,
    CsrfCookieView,
    LoginView,
    LogoutView,
    MeView,
)

urlpatterns = [
    path('csrf/', CsrfCookieView.as_view(), name='csrf-cookie'),
    path('login/', LoginView.as_view(), name='login'),
    path('browser-login/', BrowserLoginView.as_view(), name='browser-login'),
    path('refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('browser-refresh/', BrowserRefreshView.as_view(), name='browser-token-refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('browser-logout/', BrowserLogoutView.as_view(), name='browser-logout'),
    path('me/', MeView.as_view(), name='me'),
]
