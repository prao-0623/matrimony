export default function LoginForm({ form, onChange, onSubmit, error, loading }) {
  return (
    <div className="auth-shell">
      <div className="auth-card">
        <div className="eyebrow">Staff Portal</div>
        <h1>Matrimony Dashboard</h1>
        <p>Sign in with your admin credentials to view the dashboard.</p>

        <form onSubmit={onSubmit} className="auth-form">
          <label>
            Email
            <input
              type="email"
              name="email"
              placeholder="admin@example.com"
              value={form.email}
              onChange={onChange}
              required
            />
          </label>

          <label>
            Password
            <input
              type="password"
              name="password"
              placeholder="••••••••"
              value={form.password}
              onChange={onChange}
              required
            />
          </label>

          {error ? <div className="error-box">{error}</div> : null}

          <button type="submit" disabled={loading}>
            {loading ? 'Signing in...' : 'Login'}
          </button>
        </form>
      </div>
    </div>
  );
}
