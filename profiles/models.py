import uuid
from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

from .storage import ProfileMediaStorage


def profile_photo_upload_path(instance, filename):
    prefix = 'profile-primary' if getattr(instance, 'primary_photo', None) else 'profile-images'
    return f'profiles/{prefix}/{filename}'


class ProfileStatus(models.TextChoices):
    DRAFT = 'DRAFT', 'Draft'
    PENDING_REVIEW = 'PENDING_REVIEW', 'Pending Review'
    APPROVED = 'APPROVED', 'Approved'
    REJECTED = 'REJECTED', 'Rejected'
    ARCHIVED = 'ARCHIVED', 'Archived'


class Gender(models.TextChoices):
    MALE = 'male', 'Male'
    FEMALE = 'female', 'Female'
    OTHER = 'other', 'Other'


class IncomeRange(models.TextChoices):
    BELOW_3_LPA = 'BELOW_3_LPA', 'Below INR 3 lakh/year'
    FROM_3_TO_5_LPA = '3_TO_5_LPA', 'INR 3-5 lakh/year'
    FROM_5_TO_10_LPA = '5_TO_10_LPA', 'INR 5-10 lakh/year'
    FROM_10_TO_20_LPA = '10_TO_20_LPA', 'INR 10-20 lakh/year'
    FROM_20_TO_50_LPA = '20_TO_50_LPA', 'INR 20-50 lakh/year'
    ABOVE_50_LPA = 'ABOVE_50_LPA', 'Above INR 50 lakh/year'
    PREFER_NOT_TO_SAY = 'PREFER_NOT_TO_SAY', 'Prefer not to say'


class Profile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile_code = models.CharField(max_length=25, unique=True)
    full_name = models.CharField(max_length=200)
    primary_photo = models.ImageField(storage=ProfileMediaStorage(), upload_to='profiles/primary/%Y/%m/%d/', blank=True, null=True)
    gender = models.CharField(max_length=20, choices=Gender.choices, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    height_cm = models.DecimalField('Height (cm)', max_digits=4, decimal_places=1, null=True, blank=True)
    weight_kg = models.DecimalField(
        'Weight (kg)',
        max_digits=5,
        decimal_places=1,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.1'))],
    )
    profession = models.CharField(max_length=120, blank=True)
    income_range = models.CharField(max_length=24, choices=IncomeRange.choices, blank=True)
    religion = models.CharField(max_length=80, blank=True)
    caste = models.CharField(max_length=80, blank=True)
    marital_status = models.CharField(max_length=30, blank=True)
    mother_tongue = models.CharField(max_length=80, blank=True)
    status = models.CharField(max_length=20, choices=ProfileStatus.choices, default=ProfileStatus.DRAFT)
    about_me = models.TextField(blank=True)
    profile_created_by = models.CharField(max_length=30, default='SELF')
    consent_status = models.CharField(max_length=30, default='PENDING')
    consent_version = models.CharField(max_length=50, blank=True)
    consent_at = models.DateTimeField(null=True, blank=True)
    created_by_name = models.CharField(max_length=200, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_profiles')
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_profiles')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    archived_at = models.DateTimeField(null=True, blank=True)
    archived_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='archived_profiles')

    class Meta:
        db_table = 'profiles'

    @property
    def photo_url(self):
        if self.primary_photo:
            return self.primary_photo.url
        return ''

    @property
    def age(self):
        if not self.date_of_birth:
            return None

        today = timezone.localdate()
        birthday_has_passed = (today.month, today.day) >= (
            self.date_of_birth.month,
            self.date_of_birth.day,
        )
        return today.year - self.date_of_birth.year - (not birthday_has_passed)

    def __str__(self):
        return f'{self.profile_code} - {self.full_name}'


class ProfileImage(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='gallery_images')
    image = models.ImageField(storage=ProfileMediaStorage(), upload_to='profiles/gallery/%Y/%m/%d/', blank=True, null=True)
    is_primary = models.BooleanField(default=False)
    caption = models.CharField(max_length=120, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'profile_images'
        ordering = ['-is_primary', 'created_at']

    def __str__(self):
        return f'{self.profile.full_name} photo'
