import { useEffect, useState } from 'react';
import LoginForm from './components/LoginForm';
import ProfileForm from './components/ProfileForm';
import ProfileDetailCard from './components/ProfileDetailCard';
import ProfileTable from './components/ProfileTable';
import StatCard from './components/StatCard';
import TopBar from './components/TopBar';
import { getImageUrl } from './utils/media';

const API = '/api';

const emptyProfileForm = {
  profile_code: '',
  full_name: '',
  gender: '',
  date_of_birth: '',
  age: '',
  height_cm: '',
  weight_kg: '',
  profession: '',
  income_range: '',
  religion: '',
  caste: '',
  marital_status: '',
  mother_tongue: '',
  status: 'DRAFT',
  about_me: '',
  primary_photo: null,
  additional_photos: [],
};

function calculateAge(dateString) {
  if (!dateString) return '';

  const [year, month, day] = dateString.split('-').map(Number);
  if (!year || !month || !day) return '';

  const today = new Date();
  let age = today.getFullYear() - year;

  if (
    today.getMonth() + 1 < month ||
    (today.getMonth() + 1 === month && today.getDate() < day)
  ) {
    age -= 1;
  }

  return age >= 0 ? String(age) : '';
}

function getProfileFormValues(profile = {}) {
  return {
    ...emptyProfileForm,
    ...profile,
    date_of_birth: profile.date_of_birth || '',
    status: profile.status || 'DRAFT',
    age: calculateAge(profile.date_of_birth || ''),
    primary_photo: null,
    additional_photos: [],
  };
}

async function getCsrfToken() {
  const response = await fetch(`${API}/auth/csrf/`, {
    credentials: 'include',
  });

  if (!response.ok) {
    throw new Error('Unable to initialize CSRF token.');
  }

  const cookie = document.cookie
    .split('; ')
    .find((item) => item.startsWith('csrftoken='));

  return cookie ? cookie.split('=')[1] : '';
}

async function request(path, options = {}) {
  const csrfToken = document.cookie
    .split('; ')
    .find((item) => item.startsWith('csrftoken='));

  const headers = {
    ...(options.headers || {}),
  };

  if (!headers['Content-Type'] && options.body && typeof options.body === 'string') {
    headers['Content-Type'] = 'application/json';
  }

  if (csrfToken) {
    headers['X-CSRFToken'] = csrfToken.split('=')[1];
  }

  const response = await fetch(`${API}${path}`, {
    credentials: 'include',
    ...options,
    headers,
  });

  if (response.status === 204 || response.status === 205) {
    return null;
  }

  const contentType = response.headers.get('content-type') || '';
  const payload = contentType.includes('application/json') ? await response.json() : await response.text();

  if (!response.ok) {
    throw new Error(payload?.detail || payload?.message || 'Request failed');
  }

  return payload;
}

function App() {
  const [form, setForm] = useState({ email: '', password: '' });
  const [user, setUser] = useState(null);
  const [profiles, setProfiles] = useState([]);
  const [selectedProfile, setSelectedProfile] = useState(null);
  const [profileForm, setProfileForm] = useState(emptyProfileForm);
  const [activeForm, setActiveForm] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const loadSession = async () => {
    try {
      const me = await request('/auth/me/');
      setUser(me);
      const data = await request('/profiles/?page=1');
      setProfiles(data.results || data || []);
    } catch (err) {
      setUser(null);
      setProfiles([]);
    }
  };

  useEffect(() => {
    const bootstrap = async () => {
      setLoading(true);
      try {
        await getCsrfToken();
        await loadSession();
      } catch (err) {
        setUser(null);
      } finally {
        setLoading(false);
      }
    };

    bootstrap();
  }, []);

  const handleChange = (event) => {
    const { name, value } = event.target;
    setForm((current) => ({ ...current, [name]: value }));
  };

  const handleLogin = async (event) => {
    event.preventDefault();
    setError('');
    setLoading(true);

    try {
      await getCsrfToken();
      await request('/auth/browser-login/', {
        method: 'POST',
        body: JSON.stringify(form),
      });
      await loadSession();
      setForm({ email: '', password: '' });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    setLoading(true);
    try {
      await request('/auth/browser-logout/', {
        method: 'POST',
      });
      setUser(null);
      setProfiles([]);
      setSelectedProfile(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const openCreateProfile = () => {
    setSelectedProfile(null);
    setActiveForm('create');
    setProfileForm(getProfileFormValues());
    setError('');
  };

  const openEditProfile = (profile) => {
    setSelectedProfile(profile);
    setActiveForm('edit');
    setProfileForm(getProfileFormValues(profile));
    setError('');
  };

  const handleProfileFormChange = (event) => {
    const { name, value, files, type } = event.target;

    if (type === 'file') {
      const nextFiles = files && files.length ? Array.from(files) : [];
      setProfileForm((current) => ({
        ...current,
        [name]: name === 'additional_photos' ? nextFiles : nextFiles[0] || null,
      }));
      return;
    }

    const nextValue = value;
    setProfileForm((current) => {
      const nextForm = { ...current, [name]: nextValue };
      if (name === 'date_of_birth') {
        nextForm.age = calculateAge(nextValue);
      }
      return nextForm;
    });
  };

  const handleProfileSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);
    setError('');

    try {
      const payload = new FormData();

      Object.entries(profileForm).forEach(([key, value]) => {
        if (value === null || value === undefined || value === '') {
          return;
        }

        if (key === 'primary_photo' && value instanceof File) {
          payload.append('primary_photo', value);
          return;
        }

        if (key === 'additional_photos') {
          if (Array.isArray(value)) {
            value.forEach((file) => payload.append('additional_photos', file));
          }
          return;
        }

        payload.append(key, value);
      });

      const isEdit = activeForm === 'edit';
      const url = isEdit ? `/profiles/${selectedProfile.id}/` : '/profiles/';

      await request(url, {
        method: isEdit ? 'PATCH' : 'POST',
        body: payload,
      });

      setProfileForm(emptyProfileForm);
      setActiveForm(null);
      setSelectedProfile(null);
      await loadSession();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleViewProfile = (profile) => {
    setSelectedProfile(profile);
    setActiveForm(null);
  };

  const handleBackToList = () => {
    setSelectedProfile(null);
    setActiveForm(null);
  };

  const profileCount = profiles.length;
  const summaryCards = [
    { label: 'Profiles', value: profileCount },
    { label: 'User role', value: user?.role || 'Guest' },
    { label: 'Status', value: user?.status || 'Offline' },
  ];

  if (!user) {
    return (
      <LoginForm
        form={form}
        onChange={handleChange}
        onSubmit={handleLogin}
        error={error}
        loading={loading}
      />
    );
  }

  if (activeForm === 'create' || activeForm === 'edit') {
    return (
      <div className="dashboard-shell">
        <TopBar user={user} onLogout={handleLogout} loading={loading} onAddProfile={openCreateProfile} />
        <ProfileForm
          form={profileForm}
          onChange={handleProfileFormChange}
          onSubmit={handleProfileSubmit}
          onCancel={handleBackToList}
          loading={loading}
          isEdit={activeForm === 'edit'}
        />
      </div>
    );
  }

  if (selectedProfile) {
    return (
      <div className="dashboard-shell">
        <TopBar user={user} onLogout={handleLogout} loading={loading} onAddProfile={openCreateProfile} />
        <ProfileDetailCard profile={selectedProfile} onBack={handleBackToList} onEdit={() => openEditProfile(selectedProfile)} />
      </div>
    );
  }

  return (
    <div className="dashboard-shell">
      <TopBar user={user} onLogout={handleLogout} loading={loading} onAddProfile={openCreateProfile} />

      <section className="stats-grid">
        {summaryCards.map((item) => (
          <StatCard key={item.label} label={item.label} value={item.value} />
        ))}
      </section>

      <ProfileTable profiles={profiles} onViewProfile={handleViewProfile} onEditProfile={openEditProfile} />
    </div>
  );
}

export default App;
