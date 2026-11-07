from io import BytesIO
from unittest.mock import patch
from datetime import date

from django.core.exceptions import PermissionDenied
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from PIL import Image
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from accounts.models import StaffUser
from profiles.models import IncomeRange, Profile, ProfileImage, ProfileStatus
from profiles.serializers import ProfileSerializer
from profiles.views import ProfileViewSet


class StaffAuthAndProfileRulesTests(TestCase):
    def test_create_superuser_sets_super_admin_role(self):
        user = StaffUser.objects.create_superuser(email='super@example.com', password='StrongPass123!')
        self.assertEqual(user.role, 'SUPER_ADMIN')
        self.assertTrue(user.is_super_admin)

    def test_profile_destroy_is_forbidden(self):
        user = StaffUser.objects.create_user(email='admin@example.com', password='StrongPass123!')
        profile = Profile.objects.create(
            profile_code='P-1001',
            full_name='Test User',
            status=ProfileStatus.DRAFT,
            created_by=user,
        )

        view = ProfileViewSet()
        request = type('Request', (), {'user': user})()

        with self.assertRaises(PermissionDenied):
            view.destroy(request, pk=str(profile.pk))


class ProfileWebUITests(TestCase):
    def setUp(self):
        self.user = StaffUser.objects.create_user(
            email='staff@example.com',
            password='StrongPass123!',
            is_staff=True,
        )
        self.client.force_login(self.user)

    def test_profile_pages_render_gender_select_and_date_picker(self):
        response = self.client.get('/profiles/add/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<select name="gender"', html=False)
        self.assertContains(response, 'value="female"', html=False)
        self.assertContains(response, '<select name="income_range"', html=False)
        self.assertContains(response, 'Personal details')
        self.assertContains(response, 'Professional details')
        self.assertContains(response, 'name="religion"', html=False)
        self.assertContains(response, 'name="caste"', html=False)
        self.assertContains(response, 'name="height_cm"', html=False)
        self.assertContains(response, 'name="weight_kg"', html=False)
        self.assertContains(response, 'min="0.1"', html=False)
        self.assertContains(response, 'name="profession"', html=False)
        self.assertContains(response, 'type="date"', html=False)
        self.assertContains(response, 'id="id_age"', html=False)

    def test_staff_can_create_and_edit_profile(self):
        response = self.client.post('/profiles/add/', {
            'profile_code': 'P-2001',
            'full_name': 'Test Candidate',
            'gender': 'female',
            'date_of_birth': '1998-04-12',
            'height_cm': '165.5',
            'weight_kg': '58.2',
            'profession': 'Software engineer',
            'income_range': IncomeRange.FROM_10_TO_20_LPA,
            'marital_status': 'Never married',
            'mother_tongue': 'Kannada',
            'status': ProfileStatus.DRAFT,
            'about_me': 'Test profile',
            'religion': 'Hindu',
            'caste': 'Example caste',
        })

        profile = Profile.objects.get(profile_code='P-2001')
        self.assertRedirects(response, '/profiles/')
        self.assertEqual(profile.created_by, self.user)
        self.assertEqual(profile.created_by_name, self.user.email)
        self.assertEqual(profile.updated_by, self.user)
        self.assertEqual(profile.updated_by_name, self.user.email)
        self.assertEqual(profile.religion, 'Hindu')
        self.assertEqual(profile.caste, 'Example caste')
        today = date.today()
        expected_age = today.year - 1998 - ((today.month, today.day) < (4, 12))
        self.assertEqual(profile.age, expected_age)
        self.assertEqual(profile.consent_status, 'PENDING')
        self.assertEqual(str(profile.height_cm), '165.5')
        self.assertEqual(str(profile.weight_kg), '58.2')
        self.assertEqual(profile.profession, 'Software engineer')
        self.assertEqual(profile.income_range, IncomeRange.FROM_10_TO_20_LPA)
        self.assertEqual(ProfileSerializer(profile).data['income_range'], IncomeRange.FROM_10_TO_20_LPA)

        response = self.client.post(f'/profiles/{profile.pk}/edit/', {
            'profile_code': 'P-2001',
            'full_name': 'Updated Candidate',
            'gender': 'female',
            'date_of_birth': '1998-04-12',
            'height_cm': '165.5',
            'weight_kg': '58.2',
            'profession': 'Product designer',
            'income_range': IncomeRange.PREFER_NOT_TO_SAY,
            'marital_status': 'Never married',
            'mother_tongue': 'Kannada',
            'status': ProfileStatus.APPROVED,
            'about_me': 'Updated profile',
        })

        profile.refresh_from_db()
        self.assertRedirects(response, '/profiles/')
        self.assertEqual(profile.full_name, 'Updated Candidate')
        self.assertEqual(profile.status, ProfileStatus.APPROVED)
        self.assertEqual(profile.updated_by, self.user)
        self.assertEqual(profile.updated_by_name, self.user.email)

    def test_website_rejects_negative_weight(self):
        response = self.client.post('/profiles/add/', {
            'profile_code': 'P-2003',
            'full_name': 'Invalid Weight Candidate',
            'weight_kg': '-1.0',
            'status': ProfileStatus.DRAFT,
        })

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form']['weight_kg'].errors)
        self.assertFalse(Profile.objects.filter(profile_code='P-2003').exists())

    def test_profile_creator_name_remains_after_staff_account_deletion(self):
        response = self.client.post('/profiles/add/', {
            'profile_code': 'P-2002',
            'full_name': 'Creator Snapshot Candidate',
            'status': ProfileStatus.DRAFT,
        })
        profile = Profile.objects.get(profile_code='P-2002')
        self.assertRedirects(response, '/profiles/')
        self.assertEqual(profile.updated_by_name, self.user.email)

        self.user.delete()
        profile.refresh_from_db()

        self.assertIsNone(profile.created_by)
        self.assertIsNone(profile.updated_by)
        self.assertEqual(profile.created_by_name, 'staff@example.com')
        self.assertEqual(profile.updated_by_name, 'staff@example.com')
        viewer = StaffUser.objects.create_user(
            email='viewer@example.com',
            password='StrongPass123!',
            is_staff=True,
        )
        self.client.force_login(viewer)
        detail_response = self.client.get(f'/profiles/{profile.pk}/')
        self.assertContains(detail_response, 'staff@example.com')

    def test_staff_can_upload_and_view_profile_photo(self):
        image_buffer = BytesIO()
        image = Image.new('RGB', (100, 100), color='blue')
        image.save(image_buffer, format='PNG')
        image_buffer.seek(0)

        uploaded_image = SimpleUploadedFile(
            'profile.png',
            image_buffer.read(),
            content_type='image/png',
        )

        response = self.client.post('/profiles/add/', {
            'profile_code': 'P-3001',
            'full_name': 'Photo Candidate',
            'gender': 'female',
            'date_of_birth': '1997-06-21',
            'height_cm': '160.0',
            'weight_kg': '55.5',
            'profession': 'Doctor',
            'income_range': IncomeRange.FROM_20_TO_50_LPA,
            'marital_status': 'Never married',
            'mother_tongue': 'Tamil',
            'status': ProfileStatus.PENDING_REVIEW,
            'about_me': 'This is a detailed profile.',
            'primary_photo': uploaded_image,
        })

        profile = Profile.objects.get(profile_code='P-3001')
        self.assertRedirects(response, '/profiles/')
        self.assertTrue(profile.primary_photo)
        self.assertIn('profile', profile.primary_photo.name)
        self.assertIn('.png', profile.primary_photo.name)

        serializer_data = ProfileSerializer(profile).data
        self.assertIn('primary_photo_url', serializer_data)
        self.assertTrue(serializer_data['primary_photo_url'])

        detail_response = self.client.get(f'/profiles/{profile.pk}/')
        self.assertEqual(detail_response.status_code, 200)
        self.assertContains(detail_response, 'Photo Candidate')

    def test_staff_can_upload_up_to_five_profile_photos(self):
        def uploaded_image(filename):
            image_buffer = BytesIO()
            Image.new('RGB', (10, 10), color='green').save(image_buffer, format='PNG')
            return SimpleUploadedFile(filename, image_buffer.getvalue(), content_type='image/png')

        initial_images = [uploaded_image(f'photo-{index}.png') for index in range(3)]
        with patch(
            'profiles.storage.ProfileMediaStorage._save',
            autospec=True,
            side_effect=lambda storage, name, content: name,
        ):
            response = self.client.post('/profiles/add/', {
                'profile_code': 'P-3003',
                'full_name': 'Gallery Candidate',
                'status': ProfileStatus.DRAFT,
                'gallery_images': initial_images,
            })
            profile = Profile.objects.get(profile_code='P-3003')
            edit_response = self.client.post(f'/profiles/{profile.pk}/edit/', {
                'profile_code': 'P-3003',
                'full_name': 'Gallery Candidate',
                'status': ProfileStatus.DRAFT,
                'gallery_images': [uploaded_image('photo-3.png'), uploaded_image('photo-4.png')],
            })

        self.assertRedirects(response, '/profiles/')
        self.assertRedirects(edit_response, '/profiles/')
        self.assertEqual(profile.gallery_images.count(), 5)
        detail_response = self.client.get(f'/profiles/{profile.pk}/')
        self.assertContains(detail_response, 'Photos')
        self.assertEqual(detail_response.content.count(b'<img '), 5)

    def test_profile_rejects_more_than_five_total_photos(self):
        def uploaded_image(filename):
            image_buffer = BytesIO()
            Image.new('RGB', (10, 10), color='green').save(image_buffer, format='PNG')
            return SimpleUploadedFile(filename, image_buffer.getvalue(), content_type='image/png')

        image_files = [uploaded_image(f'photo-{index}.png') for index in range(6)]
        response = self.client.post('/profiles/add/', {
            'profile_code': 'P-3004',
            'full_name': 'Too Many Photos',
            'status': ProfileStatus.DRAFT,
            'gallery_images': image_files,
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'A profile can have no more than 5 photos total.')
        self.assertFalse(Profile.objects.filter(profile_code='P-3004').exists())

    def test_staff_can_view_single_profile_details(self):
        profile = Profile.objects.create(
            profile_code='P-3002',
            full_name='Single Profile Candidate',
            gender='female',
            date_of_birth='1997-06-21',
            height_cm='160.0',
            weight_kg='55.5',
            profession='Doctor',
            income_range=IncomeRange.FROM_20_TO_50_LPA,
            marital_status='Never married',
            mother_tongue='Tamil',
            status=ProfileStatus.PENDING_REVIEW,
            about_me='This is a detailed profile.',
            created_by=self.user,
        )

        response = self.client.get(f'/profiles/{profile.pk}/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Single Profile Candidate')
        self.assertContains(response, 'Doctor')
        self.assertContains(response, 'Age')
        self.assertContains(response, 'Pending Review')
        self.assertContains(response, 'This is a detailed profile.')

    def test_profile_pages_require_staff_login(self):
        self.client.logout()

        response = self.client.get('/profiles/')

        self.assertRedirects(response, '/admin/login/?next=/profiles/')


class ProfileAPITests(APITestCase):
    def setUp(self):
        self.user = StaffUser.objects.create_user(
            email='api-admin@example.com',
            password='StrongPass123!',
            is_staff=True,
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_profile_api_list_create_retrieve_and_patch(self):
        create_response = self.client.post('/api/profiles/', {
            'profile_code': 'API-1001',
            'full_name': 'API Candidate',
            'status': ProfileStatus.DRAFT,
        }, format='json')

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        profile_id = create_response.data['id']
        self.assertEqual(str(create_response.data['created_by']), str(self.user.pk))
        self.assertEqual(create_response.data['created_by_name'], self.user.email)
        self.assertEqual(create_response.data['updated_by_name'], self.user.email)

        list_response = self.client.get('/api/profiles/?search=API Candidate')
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(list_response.data['count'], 1)

        detail_response = self.client.get(f'/api/profiles/{profile_id}/')
        self.assertEqual(detail_response.status_code, status.HTTP_200_OK)

        patch_response = self.client.patch(
            f'/api/profiles/{profile_id}/',
            {'profession': 'Engineer'},
            format='json',
        )
        self.assertEqual(patch_response.status_code, status.HTTP_200_OK)
        self.assertEqual(patch_response.data['profession'], 'Engineer')
        self.assertEqual(patch_response.data['updated_by_name'], self.user.email)
        self.assertEqual(str(patch_response.data['updated_by']), str(self.user.pk))

        invalid_weight_response = self.client.patch(
            f'/api/profiles/{profile_id}/',
            {'weight_kg': '-1.0'},
            format='json',
        )
        self.assertEqual(invalid_weight_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('weight_kg', invalid_weight_response.data)

    def test_profile_api_requires_authentication(self):
        self.client.force_authenticate(user=None)

        response = self.client.get('/api/profiles/')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_api_accepts_gallery_photos_as_multipart(self):
        def uploaded_image(filename):
            image_buffer = BytesIO()
            Image.new('RGB', (10, 10), color='green').save(image_buffer, format='PNG')
            return SimpleUploadedFile(filename, image_buffer.getvalue(), content_type='image/png')

        with patch(
            'profiles.storage.ProfileMediaStorage._save',
            autospec=True,
            side_effect=lambda storage, name, content: name,
        ):
            response = self.client.post('/api/profiles/', {
                'profile_code': 'API-1002',
                'full_name': 'API Photo Candidate',
                'status': ProfileStatus.DRAFT,
                'additional_photos': [uploaded_image('api-photo-1.png'), uploaded_image('api-photo-2.png')],
            }, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(len(response.data['gallery_images']), 2)
        self.assertNotIn('additional_photos', response.data)
