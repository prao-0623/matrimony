from django.utils import timezone


def generate_biodata(profile):
    """Generate a minimal biodata payload for the initial release.

    This is intentionally lightweight and focuses on the requirement that PDFs
    are generated server-side and only include approved fields. In production,
    this function would call a PDF renderer with a template and private storage.
    """
    return {
        'profile_code': profile.profile_code,
        'full_name': profile.full_name,
        'gender': profile.gender,
        'date_of_birth': profile.date_of_birth,
        'mother_tongue': profile.mother_tongue,
        'status': profile.status,
        'generated_at': timezone.now(),
        'approved_fields_only': True,
    }
