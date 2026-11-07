from django.db import transaction
from rest_framework import serializers

from .models import Profile, ProfileImage


class ProfileImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = ProfileImage
        fields = ['id', 'image', 'image_url', 'is_primary', 'caption', 'created_at']
        read_only_fields = fields

    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return ''


class ProfileSerializer(serializers.ModelSerializer):
    age = serializers.ReadOnlyField()
    gallery_images = ProfileImageSerializer(many=True, read_only=True)
    primary_photo_url = serializers.SerializerMethodField()
    additional_photos = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False,
        allow_empty=True,
    )

    class Meta:
        model = Profile
        fields = [
            'id',
            'profile_code',
            'full_name',
            'primary_photo',
            'primary_photo_url',
            'gallery_images',
            'additional_photos',
            'gender',
            'date_of_birth',
            'age',
            'height_cm',
            'weight_kg',
            'profession',
            'income_range',
            'religion',
            'caste',
            'marital_status',
            'mother_tongue',
            'status',
            'about_me',
            'profile_created_by',
            'consent_status',
            'consent_version',
            'consent_at',
            'created_by_name',
            'created_by',
            'updated_by_name',
            'updated_by',
            'assigned_to',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'created_by_name',
            'created_by',
            'updated_by_name',
            'updated_by',
            'created_at',
            'updated_at',
        ]

    def get_primary_photo_url(self, obj):
        if obj.primary_photo:
            return obj.primary_photo.url
        return ''

    def validate(self, attrs):
        additional_photos = attrs.get('additional_photos', [])
        primary_photo = attrs.get('primary_photo')
        if self.instance and 'primary_photo' not in attrs:
            primary_photo = self.instance.primary_photo

        existing_gallery_count = self.instance.gallery_images.count() if self.instance else 0
        total_photos = bool(primary_photo) + existing_gallery_count + len(additional_photos)
        if total_photos > 5:
            raise serializers.ValidationError({
                'additional_photos': 'A profile can have no more than 5 photos total.'
            })
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        additional_photos = validated_data.pop('additional_photos', [])
        profile = super().create(validated_data)
        ProfileImage.objects.bulk_create([
            ProfileImage(profile=profile, image=image)
            for image in additional_photos
        ])
        return profile

    @transaction.atomic
    def update(self, instance, validated_data):
        additional_photos = validated_data.pop('additional_photos', [])
        profile = super().update(instance, validated_data)
        ProfileImage.objects.bulk_create([
            ProfileImage(profile=profile, image=image)
            for image in additional_photos
        ])
        return profile
