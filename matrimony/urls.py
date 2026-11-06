"""
URL configuration for matrimony project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import HttpResponseForbidden
from django.shortcuts import render
from django.urls import include, path

from profiles.models import Profile, ProfileStatus


@login_required(login_url='/admin/login/')
def home(request):
    user = request.user
    can_manage_profiles = (
        user.is_superuser
        or getattr(user, 'is_admin', False)
        or getattr(user, 'is_super_admin', False)
    )
    if not user.is_staff or not can_manage_profiles:
        return HttpResponseForbidden('You do not have access to this dashboard.')

    status_counts = dict(
        Profile.objects.values('status').annotate(total=Count('id')).values_list('status', 'total')
    )
    context = {
        'total_profiles': sum(status_counts.values()),
        'draft_count': status_counts.get(ProfileStatus.DRAFT, 0),
        'pending_review_count': status_counts.get(ProfileStatus.PENDING_REVIEW, 0),
        'approved_count': status_counts.get(ProfileStatus.APPROVED, 0),
        'recent_profiles': Profile.objects.order_by('-created_at')[:8],
    }
    return render(request, 'profiles/dashboard.html', context)


urlpatterns = [
    path('', home, name='home'),
    path('profiles/', include('profiles.web_urls')),
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
]
