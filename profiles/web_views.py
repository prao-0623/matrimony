from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ProfileForm
from .models import Profile, ProfileImage, ProfileStatus


def _save_gallery_images(form, profile):
    for image in form.cleaned_data.get('gallery_images', []):
        ProfileImage.objects.create(profile=profile, image=image)


def profile_manager_required(view_func):
    @login_required(login_url='/admin/login/')
    @wraps(view_func)
    def wrapped(request, *args, **kwargs):
        user = request.user
        can_manage = (
            user.is_staff
            and (
                user.is_superuser
                or getattr(user, 'is_admin', False)
                or getattr(user, 'is_super_admin', False)
            )
        )
        if not can_manage:
            return HttpResponseForbidden('You do not have access to profile management.')
        return view_func(request, *args, **kwargs)

    return wrapped


@profile_manager_required
def profile_list(request):
    profiles = Profile.objects.all().order_by('-created_at')
    query = request.GET.get('q', '').strip()
    selected_status = request.GET.get('status', '')

    if query:
        profiles = profiles.filter(
            Q(profile_code__icontains=query)
            | Q(full_name__icontains=query)
            | Q(profession__icontains=query)
            | Q(mother_tongue__icontains=query)
        )
    if selected_status in ProfileStatus.values:
        profiles = profiles.filter(status=selected_status)

    page = Paginator(profiles, 15).get_page(request.GET.get('page'))
    return render(request, 'profiles/profile_list.html', {
        'page': page,
        'query': query,
        'selected_status': selected_status,
        'statuses': ProfileStatus.choices,
    })


@profile_manager_required
def profile_create(request):
    form = ProfileForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        profile = form.save(commit=False)
        profile.created_by = request.user
        creator_name = request.user.get_full_name().strip() or request.user.email
        profile.created_by_name = creator_name
        profile.updated_by = request.user
        profile.updated_by_name = creator_name
        profile.save()
        _save_gallery_images(form, profile)
        messages.success(request, f'{profile.full_name} was added.')
        return redirect('web-profile-list')
    return render(request, 'profiles/profile_form.html', {'form': form, 'is_edit': False})


@profile_manager_required
def profile_detail(request, pk):
    profile = get_object_or_404(Profile, pk=pk)
    return render(request, 'profiles/profile_detail.html', {
        'profile': profile,
        'statuses': ProfileStatus.choices,
    })


@profile_manager_required
def profile_edit(request, pk):
    profile = get_object_or_404(Profile, pk=pk)
    form = ProfileForm(request.POST or None, request.FILES or None, instance=profile)
    if request.method == 'POST' and form.is_valid():
        profile = form.save()
        profile.updated_by = request.user
        profile.updated_by_name = request.user.get_full_name().strip() or request.user.email
        profile.save(update_fields=['updated_by', 'updated_by_name'])
        _save_gallery_images(form, profile)
        messages.success(request, f'{profile.full_name} was updated.')
        return redirect('web-profile-list')
    return render(request, 'profiles/profile_form.html', {
        'form': form,
        'is_edit': True,
        'profile': profile,
    })