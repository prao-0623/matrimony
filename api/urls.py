from django.urls import include, path

from accounts.views import StaffAdminListCreateAPIView

urlpatterns = [
    path('auth/', include('accounts.urls')),
    path('admins/', StaffAdminListCreateAPIView.as_view(), name='admin-list-create'),
    path('profiles/', include('profiles.urls')),
]
