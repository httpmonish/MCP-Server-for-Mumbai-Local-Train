import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';

interface LoginPageProps {
  onLoginSuccess: (user: {
    name: string;
    org: string;
    role: string;
    token: string;
    prn?: string;
    semester?: string;
    utsPassId?: string;
  }) => void;
}

export const LoginPage: React.FC<LoginPageProps> = ({ onLoginSuccess }) => {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [showPassword, setShowPassword] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!email.trim() || !password.trim()) {
      setError('Please enter both email and password.');
      return;
    }

    setIsLoading(true);

    // Simulate auth delay
    await new Promise((res) => setTimeout(res, 1200));

    // Mock authentication
    if (email.includes('@') && password.length >= 4) {
      const namePart = email.split('@')[0];
      const displayName = namePart.charAt(0).toUpperCase() + namePart.slice(1);
      const isStudent = email.includes('vjti') || email.includes('edu') || email.includes('college');

      onLoginSuccess({
        name: displayName,
        org: isStudent ? 'VJTI, Matunga' : 'Mumbai Suburban Commuter Network',
        role: isStudent ? 'Student' : 'Commuter',
        token: `jwt_${Date.now()}_${Math.random().toString(36).slice(2)}`,
        prn: isStudent ? `VJTI-${Math.floor(Math.random() * 90000 + 10000)}` : undefined,
        semester: isStudent ? 'Sem VI' : undefined,
        utsPassId: `UTS-CR-${Math.floor(Math.random() * 90000 + 10000)}`,
      });
      navigate('/trains');
    } else {
      setError('Invalid credentials. Use any email with 4+ char password.');
    }

    setIsLoading(false);
  };

  return (
    <div className="min-h-screen bg-[#080c14] text-white font-body flex flex-col relative overflow-hidden">
      {/* Grid Background */}
      <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.015)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.015)_1px,transparent_1px)] bg-[size:60px_60px] pointer-events-none" />

      {/* Red glow */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[600px] h-[400px] bg-[radial-gradient(ellipse,rgba(220,38,38,0.12)_0%,transparent_60%)] pointer-events-none" />

      {/* Navigation */}
      <nav className="relative z-20 w-full px-6 py-5 flex items-center justify-between max-w-[1400px] mx-auto">
        <Link to="/" className="flex items-baseline gap-1.5">
          <span className="font-headline text-xl tracking-tight text-white/90">
            मुंबई<span className="font-body text-sm font-semibold text-[#DC2626] tracking-normal">Teleport</span>
          </span>
        </Link>
        <Link
          to="/register"
          className="font-mono text-[11px] text-white/50 hover:text-white transition-colors tracking-wider uppercase"
        >
          Create Account →
        </Link>
      </nav>

      {/* Login Card */}
      <div className="relative z-10 flex-1 flex items-center justify-center px-6 pb-12">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="w-full max-w-md"
        >
          <div className="text-center mb-8">
            <h1 className="font-headline text-3xl sm:text-4xl tracking-tight text-white/90 mb-2">Welcome Back</h1>
            <p className="font-body text-sm text-white/35">Sign in to access your suburban commute dashboard</p>
          </div>

          <form onSubmit={handleSubmit} className="p-6 rounded-3xl bg-white/[0.02] border border-white/[0.06] backdrop-blur-xl flex flex-col gap-5">
            {/* Email */}
            <div className="flex flex-col gap-1.5">
              <label className="font-mono text-[10px] text-white/40 tracking-wider uppercase">Email or Mobile</label>
              <div className="relative">
                <span className="absolute left-4 top-1/2 -translate-y-1/2 material-symbols-outlined text-[18px] text-white/25">mail</span>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="commuter@mumbai.railway"
                  className="w-full pl-11 pr-4 py-3 rounded-xl bg-white/[0.03] border border-white/[0.08] focus:border-[#DC2626]/50 outline-none font-body text-sm text-white/90 placeholder:text-white/20 transition-colors"
                  autoComplete="email"
                />
              </div>
            </div>

            {/* Password */}
            <div className="flex flex-col gap-1.5">
              <label className="font-mono text-[10px] text-white/40 tracking-wider uppercase">Password</label>
              <div className="relative">
                <span className="absolute left-4 top-1/2 -translate-y-1/2 material-symbols-outlined text-[18px] text-white/25">lock</span>
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full pl-11 pr-12 py-3 rounded-xl bg-white/[0.03] border border-white/[0.08] focus:border-[#DC2626]/50 outline-none font-body text-sm text-white/90 placeholder:text-white/20 transition-colors"
                  autoComplete="current-password"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 w-7 h-7 rounded-lg bg-white/[0.04] hover:bg-white/[0.08] flex items-center justify-center cursor-pointer transition-colors"
                >
                  <span className="material-symbols-outlined text-[16px] text-white/40">
                    {showPassword ? 'visibility_off' : 'visibility'}
                  </span>
                </button>
              </div>
            </div>

            {/* Error */}
            {error && (
              <motion.div
                initial={{ opacity: 0, y: -4 }}
                animate={{ opacity: 1, y: 0 }}
                className="p-3 rounded-xl bg-red-500/10 border border-red-500/20 flex items-center gap-2"
              >
                <span className="material-symbols-outlined text-[16px] text-red-400">error</span>
                <span className="font-mono text-[11px] text-red-400">{error}</span>
              </motion.div>
            )}

            {/* Submit */}
            <button
              type="submit"
              disabled={isLoading}
              className="w-full py-3.5 rounded-xl bg-[#DC2626] hover:bg-[#EF4444] disabled:opacity-60 text-white font-body text-sm font-semibold transition-all shadow-[0_4px_20px_rgba(220,38,38,0.3)] hover:shadow-[0_8px_32px_rgba(220,38,38,0.4)] flex items-center justify-center gap-2 cursor-pointer disabled:cursor-wait"
            >
              {isLoading ? (
                <>
                  <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  <span>Authenticating...</span>
                </>
              ) : (
                <>
                  <span>Sign In</span>
                  <span className="material-symbols-outlined text-[18px]">login</span>
                </>
              )}
            </button>

            {/* Divider */}
            <div className="flex items-center gap-3">
              <div className="flex-1 h-px bg-white/[0.06]" />
              <span className="font-mono text-[9px] text-white/20 tracking-wider uppercase">Or continue as</span>
              <div className="flex-1 h-px bg-white/[0.06]" />
            </div>

            {/* Guest Mode */}
            <Link
              to="/trains"
              className="w-full py-3 rounded-xl bg-white/[0.03] hover:bg-white/[0.06] border border-white/[0.06] hover:border-white/[0.12] text-white/60 hover:text-white font-body text-sm transition-all flex items-center justify-center gap-2"
            >
              <span className="material-symbols-outlined text-[18px] text-white/40">person</span>
              <span>Guest Commuter Mode</span>
            </Link>
          </form>

          {/* Register Link */}
          <p className="text-center mt-6 font-body text-xs text-white/30">
            New to मुंबईTeleport?{' '}
            <Link to="/register" className="text-[#DC2626] hover:text-[#EF4444] transition-colors font-medium">
              Create Account
            </Link>
          </p>
        </motion.div>
      </div>
    </div>
  );
};

export default LoginPage;
