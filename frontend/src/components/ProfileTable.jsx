import { getImageUrl, getInitials } from '../utils/media';

export default function ProfileTable({ profiles, onViewProfile, onEditProfile }) {
  return (
    <section className="panel">
      <div className="panel-header">
        <h2>Profile Overview</h2>
        <span>{profiles.length} records</span>
      </div>

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Profile</th>
              <th>Profession</th>
              <th>Status</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {profiles.length ? (
              profiles.slice(0, 8).map((profile) => (
                <tr key={profile.id || profile.profile_code}>
                  <td>
                    <div className="profile-cell">
                      <div className="mini-avatar">
                        {getImageUrl(profile.primary_photo_url || profile.primary_photo) ? (
                          <img src={getImageUrl(profile.primary_photo_url || profile.primary_photo)} alt={profile.full_name} />
                        ) : (
                          <span>{getInitials(profile.full_name)}</span>
                        )}
                      </div>
                      <div>
                        <strong>{profile.full_name || profile.profile_code}</strong>
                        <small>{profile.profile_code}</small>
                      </div>
                    </div>
                  </td>
                  <td>{profile.profession || '—'}</td>
                  <td>
                    <span className="status-pill">{profile.status || 'ACTIVE'}</span>
                  </td>
                  <td>
                    <div className="action-group">
                      <button type="button" className="table-btn" onClick={() => onViewProfile(profile)}>
                        View
                      </button>
                      <button type="button" className="secondary-btn small-btn" onClick={() => onEditProfile(profile)}>
                        Edit
                      </button>
                    </div>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="4" className="empty-row">
                  No profiles available yet.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}
