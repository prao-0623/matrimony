from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from .models import StaffRole, StaffStatus

User = get_user_model()


class StaffAuthAPITests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.superuser = User.objects.create_superuser(
            email='super@example.com',
            password='StrongPass123!',
        )
        self.admin = User.objects.create_user(
            email='admin@example.com',
            password='StrongPass123!',
            role=StaffRole.ADMIN,
            status=StaffStatus.ACTIVE,
        )

    def test_login_returns_tokens_and_user_details(self):
        response = self.client.post(
            '/api/auth/login/',
            {'email': 'admin@example.com', 'password': 'StrongPass123!'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['access'])
        self.assertTrue(response.data['refresh'])
        self.assertEqual(response.data['user']['email'], 'admin@example.com')
        self.assertEqual(response.data['user']['role'], StaffRole.ADMIN)

    def test_refresh_and_logout_revoke_refresh_token(self):
        login_response = self.client.post(
            '/api/auth/login/',
            {'email': 'admin@example.com', 'password': 'StrongPass123!'},
            format='json',
        )
        refresh = login_response.data['refresh']

        refresh_response = self.client.post(
            '/api/auth/refresh/', {'refresh': refresh}, format='json'
        )
        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)
        self.assertTrue(refresh_response.data['access'])
        rotated_refresh = refresh_response.data['refresh']

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {refresh_response.data['access']}"
        )
        logout_response = self.client.post(
            '/api/auth/logout/', {'refresh': rotated_refresh}, format='json'
        )
        self.assertEqual(logout_response.status_code, status.HTTP_205_RESET_CONTENT)

        revoked_refresh_response = self.client.post(
            '/api/auth/refresh/', {'refresh': rotated_refresh}, format='json'
        )
        self.assertEqual(revoked_refresh_response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_disabled_staff_cannot_log_in(self):
        self.admin.status = StaffStatus.DISABLED
        self.admin.save(update_fields=['status'])

        response = self.client.post(
            '/api/auth/login/',
            {'email': 'admin@example.com', 'password': 'StrongPass123!'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_browser_login_sets_cookie_tokens(self):
        response = self.client.post(
            '/api/auth/browser-login/',
            {'email': 'admin@example.com', 'password': 'StrongPass123!'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access_token', response.cookies)
        self.assertIn('refresh_token', response.cookies)
        self.assertTrue(response.cookies['access_token']['httponly'])
        self.assertTrue(response.cookies['refresh_token']['httponly'])

    def test_browser_refresh_uses_cookie_refresh_token(self):
        self.client.post(
            '/api/auth/browser-login/',
            {'email': 'admin@example.com', 'password': 'StrongPass123!'},
            format='json',
        )

        response = self.client.post('/api/auth/browser-refresh/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access_token', response.cookies)

    def test_superadmin_can_create_admin(self):
        self.client.force_authenticate(user=self.superuser)
        response = self.client.post(
            '/api/admins/',
            {
                'email': 'newadmin@example.com',
                'password': 'NewStrongPass123!',
                'first_name': 'New',
                'last_name': 'Admin',
                'role': StaffRole.ADMIN,
                'status': StaffStatus.ACTIVE,
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email='newadmin@example.com').exists())

    def test_admin_cannot_create_admin(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(
            '/api/admins/',
            {
                'email': 'blocked@example.com',
                'password': 'NewStrongPass123!',
                'role': StaffRole.ADMIN,
                'status': StaffStatus.ACTIVE,
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
