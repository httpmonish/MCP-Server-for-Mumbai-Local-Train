import React, { useState } from 'react';

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  onLoginSuccess: (user: { name: string; org: string; role: string; token: string }) => void;
}

export const AuthModal: React.FC<AuthModalProps> = ({ isOpen, onClose, onLoginSuccess }) => {
  const [mode, setMode] = useState<'login' | 'register'>('login');
  const [email, setEmail] = useState('aditya@vjti.ac.in');
  const [password, setPassword] = useState('StudentPassword123!');
  const [fullName, setFullName] = useState('Aditya Sharma');
  const [orgName, setOrgName] = useState('VJTI Mumbai');
  const [orgType, setOrgType] = useState('COLLEGE');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      if (mode === 'login') {
        const res = await fetch('http://localhost:8000/auth/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, password }),
        });
        if (!res.ok) {
          const data = await res.json();
          throw new Error(data.detail || 'Login failed.');
        }
        const data = await res.json();
        onLoginSuccess({
          name: data.user.full_name || data.user.email,
          org: data.organization.name,
          role: data.user.role,
          token: data.tokens.access_token,
        });
        onClose();
      } else {
        const res = await fetch('http://localhost:8000/auth/register', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            email,
            password,
            full_name: fullName,
            org_name: orgName,
            org_type: orgType,
          }),
        });
        if (!res.ok) {
          const data = await res.json();
          throw new Error(data.detail || 'Registration failed.');
        }
        const data = await res.json();
        onLoginSuccess({
          name: data.user.full_name || data.user.email,
          org: data.organization.name,
          role: data.user.role,
          token: data.tokens.access_token,
        });
        onClose();
      }
    } catch (err: any) {
      setError(err.message || 'An error occurred.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
      <div className="relative w-full max-w-md p-6 rounded-3xl bg-surface-obsidian border border-glass-border shadow-2xl text-text-primary">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-text-muted hover:text-white transition-colors"
        >
          <span className="material-symbols-outlined text-[20px]">close</span>
        </button>

        <div className="flex flex-col mb-4">
          <span className="font-headline text-2xl">
            {mode === 'login' ? 'Sign In to मुंबईTeleport' : 'Register Organization'}
          </span>
          <span className="font-mono text-xs text-text-muted">
            {mode === 'login'
              ? 'Access real-time schedules, biometric radar, and delay passes'
              : 'Create tenant organization & admin account'}
          </span>
        </div>

        {error && (
          <div className="p-3 mb-4 rounded-xl bg-signal-rose/10 border border-signal-rose/30 text-signal-rose font-mono text-xs">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="flex flex-col gap-3">
          {mode === 'register' && (
            <>
              <div>
                <label className="font-mono text-[10px] uppercase text-text-muted">Full Name</label>
                <input
                  type="text"
                  required
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  className="w-full mt-1 px-3 py-2 rounded-xl bg-white/[0.04] border border-glass-border font-body text-xs text-white focus:outline-none focus:border-primary"
                />
              </div>
              <div>
                <label className="font-mono text-[10px] uppercase text-text-muted">Organization Name</label>
                <input
                  type="text"
                  required
                  value={orgName}
                  onChange={(e) => setOrgName(e.target.value)}
                  className="w-full mt-1 px-3 py-2 rounded-xl bg-white/[0.04] border border-glass-border font-body text-xs text-white focus:outline-none focus:border-primary"
                />
              </div>
              <div>
                <label className="font-mono text-[10px] uppercase text-text-muted">Organization Type</label>
                <select
                  value={orgType}
                  onChange={(e) => setOrgType(e.target.value)}
                  className="w-full mt-1 px-3 py-2 rounded-xl bg-surface-container-high border border-glass-border font-body text-xs text-white focus:outline-none focus:border-primary"
                >
                  <option value="COLLEGE">COLLEGE (College / University)</option>
                  <option value="COMPANY">COMPANY (Corporate / Shift Worker)</option>
                  <option value="HOTEL">HOTEL (Hospitality)</option>
                  <option value="OTHER">OTHER</option>
                </select>
              </div>
            </>
          )}

          <div>
            <label className="font-mono text-[10px] uppercase text-text-muted">Email Address</label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full mt-1 px-3 py-2 rounded-xl bg-white/[0.04] border border-glass-border font-body text-xs text-white focus:outline-none focus:border-primary"
            />
          </div>

          <div>
            <label className="font-mono text-[10px] uppercase text-text-muted">Password</label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full mt-1 px-3 py-2 rounded-xl bg-white/[0.04] border border-glass-border font-body text-xs text-white focus:outline-none focus:border-primary"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full mt-3 py-2.5 rounded-full bg-primary-container text-black font-body text-xs font-semibold hover:bg-primary transition-all flex items-center justify-center gap-2 cursor-pointer shadow-lg shadow-primary-container/20"
          >
            <span>{loading ? 'Processing...' : mode === 'login' ? 'Sign In' : 'Create Organization'}</span>
          </button>
        </form>

        <div className="mt-4 pt-3 border-t border-glass-border flex items-center justify-between font-mono text-[11px] text-text-muted">
          <span>{mode === 'login' ? "Don't have an org?" : 'Already registered?'}</span>
          <button
            type="button"
            onClick={() => {
              setMode(mode === 'login' ? 'register' : 'login');
              setError(null);
            }}
            className="text-primary hover:underline"
          >
            {mode === 'login' ? 'Register Org →' : 'Sign In →'}
          </button>
        </div>
      </div>
    </div>
  );
};
