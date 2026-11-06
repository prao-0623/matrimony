export default function TopBar({ user, onLogout, loading, onAddProfile }) {
  return (
    <header className="topbar">
      <div>
        <div className="eyebrow">Dashboard</div>
        <h1>Welcome back, {user?.first_name || user?.email || 'Admin'}</h1>
      </div>
      <div className="topbar-actions">
        <button type="button" className="secondary-btn" onClick={onAddProfile} disabled={loading}>
          Add profile
        </button>
        <button className="ghost-btn" onClick={onLogout} disabled={loading}>
          Logout
        </button>
      </div>
    </header>
  );
}
