from django.core.exceptions import PermissionDenied
from rest_framework.filters import SearchFilter
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from accounts.permissions import IsAdminOrSuperAdmin
from .models import Profile
from .serializers import ProfileSerializer


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.select_related(
        'created_by', 'assigned_to', 'archived_by'
    ).prefetch_related('gallery_images').order_by('-created_at', '-id')
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated, IsAdminOrSuperAdmin]
    filter_backends = [SearchFilter]
    search_fields = ['profile_code', 'full_name', 'profession', 'mother_tongue']

    def perform_create(self, serializer):
        creator = self.request.user
        serializer.save(
            created_by=creator,
            created_by_name=creator.get_full_name().strip() or creator.email,
        )

    def destroy(self, request, *args, **kwargs):
        raise PermissionDenied('Profiles cannot be permanently deleted. Use archive or status changes instead.')
