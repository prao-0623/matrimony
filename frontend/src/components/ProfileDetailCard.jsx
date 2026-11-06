import { getImageUrl, getInitials } from '../utils/media';

export default function ProfileDetailCard({ profile, onBack, onEdit }) {
  const primaryPhoto = getImageUrl(profile?.primary_photo_url || profile?.primary_photo);
  const galleryImages = Array.isArray(profile?.gallery_images) ? profile.gallery_images.map((image) => getImageUrl(image?.image_url || image?.image)).filter(Boolean) : [];

  const fields = [
    { label: 'Full name', value: profile?.full_name || '—' },
    { label: 'Profile code', value: profile?.profile_code || '—' },
    { label: 'Gender', value: profile?.gender || '—' },
    { label: 'Date of birth', value: profile?.date_of_birth || '—' },
    { label: 'Age', value: profile?.age ?? '—' },
    { label: 'Height', value: profile?.height_cm ? `${profile.height_cm} cm` : '—' },
    { label: 'Weight', value: profile?.weight_kg ? `${profile.weight_kg} kg` : '—' },
    { label: 'Profession', value: profile?.profession || '—' },
    { label: 'Income range', value: profile?.income_range || '—' },
    { label: 'Religion', value: profile?.religion || '—' },
    { label: 'Caste', value: profile?.caste || '—' },
    { label: 'Marital status', value: profile?.marital_status || '—' },
    { label: 'Mother tongue', value: profile?.mother_tongue || '—' },
    { label: 'Status', value: profile?.status || 'DRAFT' },
  ];

  return (
    <section className="profile-detail-shell">
      <div className="profile-detail-card">
        <div className="detail-header">
          <div>
            <div className="eyebrow accent">Profile</div>
            <h2>{profile?.full_name || 'Profile Details'}</h2>
          </div>
          <div className="detail-actions">
            <button type="button" className="secondary-btn" onClick={onBack}>
              Back to list
            </button>
            {onEdit && (
              <button type="button" className="table-btn" onClick={onEdit}>
                Edit profile
              </button>
            )}
          </div>
        </div>

        <div className="profile-hero">
          <div className="avatar-ring">
            {primaryPhoto ? (
              <img src={primaryPhoto} alt={profile?.full_name || 'Profile'} />
            ) : (
              getInitials(profile?.full_name)
            )}
          </div>
          <div className="hero-meta">
            <span className="badge">{profile?.status || 'ACTIVE'}</span>
            <p>{profile?.profession || 'Professional'}</p>
          </div>
        </div>

        {(primaryPhoto || galleryImages.length > 0) && (
          <div className="photo-gallery">
            {primaryPhoto && <img src={primaryPhoto} alt={profile?.full_name || 'Profile'} className="gallery-photo main-photo" />}
            {galleryImages.map((image, index) => (
              <img key={`${image}-${index}`} src={image} alt={`${profile?.full_name || 'Profile'} ${index + 1}`} className="gallery-photo" />
            ))}
          </div>
        )}

        <div className="detail-grid">
          {fields.map((field) => (
            <div key={field.label} className="detail-item">
              <span>{field.label}</span>
              <strong>{field.value}</strong>
            </div>
          ))}
        </div>

        {profile?.about_me && (
          <div className="about-box">
            <span>About me</span>
            <p>{profile.about_me}</p>
          </div>
        )}
      </div>
    </section>
  );
}
