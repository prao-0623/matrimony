from django.urls import path

from .views import ProfileViewSet

urlpatterns = [
    path('', ProfileViewSet.as_view({'get': 'list', 'post': 'create'}), name='profile-list'),
    path('<uuid:pk>/', ProfileViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update'}), name='profile-detail'),
]
