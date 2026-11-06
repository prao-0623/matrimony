from django import forms

from .models import Profile


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleImageField(forms.ImageField):
    widget = MultipleFileInput

    def clean(self, data, initial=None):
        if not data:
            return []
        if not isinstance(data, (list, tuple)):
            data = [data]
        return [forms.ImageField.clean(self, image, initial) for image in data]


class ProfileForm(forms.ModelForm):
    age = forms.CharField(label='Age', required=False, disabled=True)
    gallery_images = MultipleImageField(
        label='Additional photos',
        required=False,
        help_text='Select additional images. A profile can have up to 5 photos total, including the primary photo.',
        widget=MultipleFileInput(attrs={'accept': 'image/*'}),
    )

    class Meta:
        model = Profile
        fields = [
            'profile_code',
            'full_name',
            'primary_photo',
            'gender',
            'date_of_birth',
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
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'id': 'id_date_of_birth'}),
            'weight_kg': forms.NumberInput(attrs={'min': '0.1', 'step': '0.1'}),
            'about_me': forms.Textarea(attrs={'rows': 4}),
            'primary_photo': forms.FileInput(attrs={'accept': 'image/*'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['age'].widget.attrs['id'] = 'id_age'
        if self.instance and self.instance.pk and self.instance.age is not None:
            self.fields['age'].initial = self.instance.age

    @property
    def sections(self):
        return [
            {
                'title': 'Personal details',
                'fields': [
                    self[name] for name in (
                        'profile_code', 'full_name', 'gender', 'date_of_birth', 'age',
                        'religion', 'caste', 'height_cm', 'weight_kg',
                        'marital_status', 'mother_tongue', 'primary_photo',
                        'gallery_images', 'about_me',
                    )
                ],
            },
            {
                'title': 'Professional details',
                'fields': [self['profession'], self['income_range']],
            },
            {
                'title': 'Profile review',
                'fields': [self['status']],
            },
        ]

    def clean(self):
        cleaned_data = super().clean()
        primary_photo = cleaned_data.get('primary_photo')
        new_gallery_images = cleaned_data.get('gallery_images', [])
        existing_gallery_count = (
            self.instance.gallery_images.count() if self.instance.pk else 0
        )
        photo_count = bool(primary_photo) + existing_gallery_count + len(new_gallery_images)

        if photo_count > 5 and (
            'primary_photo' in self.changed_data or 'gallery_images' in self.changed_data
        ):
            error_field = 'gallery_images' if new_gallery_images else 'primary_photo'
            self.add_error(error_field, 'A profile can have no more than 5 photos total.')

        return cleaned_data