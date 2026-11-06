from django.urls import path

from . import web_views

urlpatterns = [
    path('', web_views.profile_list, name='web-profile-list'),
    path('add/', web_views.profile_create, name='web-profile-add'),
    path('<uuid:pk>/', web_views.profile_detail, name='web-profile-detail'),
    path('<uuid:pk>/edit/', web_views.profile_edit, name='web-profile-edit'),
]