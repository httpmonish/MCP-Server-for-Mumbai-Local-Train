import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';

interface RegisterPageProps {
  onRegisterSuccess: (user: {
    name: string;
    org: string;
    role: string;
    token: string;
    prn?: string;
    semester?: string;
    utsPassId?: string;
  }) => void;
}

export const RegisterPage: React.FC<RegisterPageProps> = ({ onRegisterSuccess }) => {
  const navigate = useNavigate();
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [accountType, setAccountType] = useState<'COMMUTER' | 'STUDENT' | 'CORPORATE'>('COMMUTER');
  const [college, setCollege] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!name.trim() || !email.trim() || !password.trim()) {
      setError('Please fill in all required fields.');
      return;
    }
    if (password.length < 4) {
      setError('Password must be at least 4 characters.');
      return;
    }

    setIsLoading(true);
    await new Promise((res) => setTimeout(res, 1500));

    const isStudent = accountType === 'STUDENT';

    onRegisterSuccess({
      name: name.trim(),
      org: isStudent ? (college || 'VJTI, Matunga') : 'Mumbai Suburban Network',
      role: accountType,
      token: `jwt_${Date.now()}_${Math.random().toString(36).slice(2)}`,
      prn: isStudent ? `VJTI-${Math.floor(Math.random() * 90000 + 10000)}` : undefined,
      semester: isStudent ? 'Sem VI' : undefined,
      utsPassId: `UTS-CR-${Math.floor(Math.random() * 90000 + 10000)}`,
    });

    navigate('/trains');
    setIsLoading(false);
  };

  return (
    <div className="min-h-screen bg-[#080c14] text-white font-body flex flex-col relative overflow-hidden">
      {/* Grid Background */}
      <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.015)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.015)_1px,transparent_1px)] bg-[size:60px_60px] pointer-events-none" />

      {/* Red glow */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[600px] h-[400px] bg-[radial-gradient(ellipse,rgba(220,38,38,0.1)_0%,transparent_60%)] pointer-events-none" />

      {/* Navigation */}
      <nav className="relative z-20 w-full px-6 py-5 flex items-center justify-between max-w-[1400px] mx-auto">
        <Link to="/" className="flex items-baseline gap-1.5">
          <span className="font-headline text-xl tracking-tight text-white/90">
            मुंबई<span className="font-body text-sm font-semibold text-[#DC2626] tracking-normal">Teleport</span>
          </span>
        </Link>
        <Link
          to="/login"
          className="font-mono text-[11px] text-white/50 hover:text-white transition-colors tracking-wider uppercase"
        >
          ← Sign In
        </Link>
      </nav>

      {/* Register Card */}
      <div className="relative z-10 flex-1 flex items-center justify-center px-6 pb-12">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="w-full max-w-md"
        >
          <div className="text-center mb-8">
            <h1 className="font-headline text-3xl sm:text-4xl tracking-tight text-white/90 mb-2">Create Account</h1>
            <p className="font-body text-sm text-white/35">Join Mumbai's suburban telemetry network</p>
          </div>

          <form onSubmit={handleSubmit} className="p-6 rounded-3xl bg-white/[0.02] border border-white/[0.06] backdrop-blur-xl flex flex-col gap-5">
            {/* Account Type */}
            <div className="flex flex-col gap-1.5">
              <label className="font-mono text-[10px] text-white/40 tracking-wider uppercase">Account Type</label>
              <div className="grid grid-cols-3 gap-1 p-1 bg-white/[0.03] rounded-xl border border-white/[0.06]">
                {(['COMMUTER', 'STUDENT', 'CORPORATE'] as const).map((type) => (
                  <button
                    key={type}
                    type="button"
                    onClick={() => setAccountType(type)}
                    className={`py-2 rounded-lg text-xs font-medium transition-all cursor-pointer ${
                      accountType === type
                        ? 'bg-[#DC2626] text-white shadow-md'
                        : 'text-white/40 hover:text-white/60'
                    }`}
                  >
                    {type === 'COMMUTER' ? 'Commuter' : type === 'STUDENT' ? 'Student' : 'Corporate'}
                  </button>
                ))}
              </div>
            </div>

            {/* Full Name */}
            <div className="flex flex-col gap-1.5">
              <label className="font-mono text-[10px] text-white/40 tracking-wider uppercase">Full Name</label>
              <div className="relative">
                <span className="absolute left-4 top-1/2 -translate-y-1/2 material-symbols-outlined text-[18px] text-white/25">person</span>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="Aditya Sharma"
                  className="w-full pl-11 pr-4 py-3 rounded-xl bg-white/[0.03] border border-white/[0.08] focus:border-[#DC2626]/50 outline-none font-body text-sm text-white/90 placeholder:text-white/20 transition-colors"
                />
              </div>
            </div>

            {/* Email */}
            <div className="flex flex-col gap-1.5">
              <label className="font-mono text-[10px] text-white/40 tracking-wider uppercase">Email</label>
              <div className="relative">
                <span className="absolute left-4 top-1/2 -translate-y-1/2 material-symbols-outlined text-[18px] text-white/25">mail</span>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder={accountType === 'STUDENT' ? 'student@vjti.ac.in' : 'user@railway.co'}
                  className="w-full pl-11 pr-4 py-3 rounded-xl bg-white/[0.03] border border-white/[0.08] focus:border-[#DC2626]/50 outline-none font-body text-sm text-white/90 placeholder:text-white/20 transition-colors"
                  autoComplete="email"
                />
              </div>
            </div>

            {/* College (conditional) */}
            {accountType === 'STUDENT' && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="flex flex-col gap-1.5"
              >
                <label className="font-mono text-[10px] text-white/40 tracking-wider uppercase">College / Institution</label>
                <div className="relative">
                  <span className="absolute left-4 top-1/2 -translate-y-1/2 material-symbols-outlined text-[18px] text-white/25">school</span>
                  <input
                    type="text"
                    value={college}
                    onChange={(e) => setCollege(e.target.value)}
                    placeholder="VJTI, Matunga"
                    className="w-full pl-11 pr-4 py-3 rounded-xl bg-white/[0.03] border border-white/[0.08] focus:border-[#DC2626]/50 outline-none font-body text-sm text-white/90 placeholder:text-white/20 transition-colors"
                  />
                </div>
              </motion.div>
            )}

            {/* Password */}
            <div className="flex flex-col gap-1.5">
              <label className="font-mono text-[10px] text-white/40 tracking-wider uppercase">Password</label>
              <div className="relative">
                <span className="absolute left-4 top-1/2 -translate-y-1/2 material-symbols-outlined text-[18px] text-white/25">lock</span>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full pl-11 pr-4 py-3 rounded-xl bg-white/[0.03] border border-white/[0.08] focus:border-[#DC2626]/50 outline-none font-body text-sm text-white/90 placeholder:text-white/20 transition-colors"
                  autoComplete="new-password"
                />
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
                  <span>Creating Account...</span>
                </>
              ) : (
                <>
                  <span>Create Account</span>
                  <span className="material-symbols-outlined text-[18px]">how_to_reg</span>
                </>
              )}
            </button>
          </form>

          {/* Login Link */}
          <p className="text-center mt-6 font-body text-xs text-white/30">
            Already have an account?{' '}
            <Link to="/login" className="text-[#DC2626] hover:text-[#EF4444] transition-colors font-medium">
              Sign In
            </Link>
          </p>
        </motion.div>
      </div>
    </div>
  );
};

export default RegisterPage;
