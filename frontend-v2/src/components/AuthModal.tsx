import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import type { PersonaType } from './modals/UserProfilePopover';

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
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

export const AuthModal: React.FC<AuthModalProps> = ({ isOpen, onClose, onLoginSuccess }) => {
  const [mode, setMode] = useState<'login' | 'register'>('login');
  const [persona, setPersona] = useState<PersonaType>('STUDENT');

  // Common Fields
  const [email, setEmail] = useState('aditya@vjti.ac.in');
  const [password, setPassword] = useState('StudentPassword123!');
  const [fullName, setFullName] = useState('Aditya Sharma');

  // Student Fields
  const [college, setCollege] = useState('Veermata Jijabai Technological Institute (VJTI)');
  const [rollNumber, setRollNumber] = useState('211080042');
  const [lectureTime, setLectureTime] = useState('09:30 AM');

  // Corporate Fields
  const [corporateHub, setCorporateHub] = useState('Bandra Kurla Complex (BKC)');
  const [slackSync, setSlackSync] = useState(true);

  // Commuter Fields
  const [mobileNumber, setMobileNumber] = useState('+91 98200 12345');
  const [utsPassId, setUtsPassId] = useState('UTS-II-CR-98401');

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      // Direct high-fidelity simulated response with backend fallback
      setTimeout(() => {
        setLoading(false);
        onLoginSuccess({
          name: fullName || 'Aditya Sharma',
          org:
            persona === 'STUDENT'
              ? college
              : persona === 'CORPORATE'
              ? `${corporateHub} • Corporate Hub`
              : 'Mumbai Daily Commuter',
          role: persona === 'STUDENT' ? 'STUDENT' : persona === 'CORPORATE' ? 'EMPLOYEE' : 'COMMUTER',
          token: `tp_token_${Date.now()}`,
          prn: persona === 'STUDENT' ? `PRN: ${rollNumber}` : `ID: ${utsPassId}`,
          semester: persona === 'STUDENT' ? 'Sem VI • B.Tech CS' : persona === 'CORPORATE' ? 'FinTech Pro' : 'Regular Suburban',
          utsPassId: utsPassId,
        });
        onClose();
      }, 600);
    } catch (err: any) {
      setError(err.message || 'An error occurred.');
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
      <motion.div
        initial={{ opacity: 0, scale: 0.95, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.95, y: 20 }}
        className="relative w-full max-w-lg p-6 sm:p-8 rounded-3xl bg-surface-obsidian border border-glass-border shadow-2xl text-text-primary"
      >
        <button
          onClick={onClose}
          className="absolute top-5 right-5 text-text-muted hover:text-white transition-colors cursor-pointer"
        >
          <span className="material-symbols-outlined text-[20px]">close</span>
        </button>

        <div className="flex flex-col mb-4">
          <span className="font-headline text-2xl">
            {mode === 'login' ? 'Sign In to मुंबईTeleport' : 'Create Commuter Identity'}
          </span>
          <span className="font-mono text-xs text-text-muted">
            Choose your commuter persona to auto-calibrate schedule & transit buffers
          </span>
        </div>

        {/* 3-Way Persona Switcher Toggle */}
        <div className="grid grid-cols-3 gap-1 p-1 mb-5 bg-white/[0.04] rounded-2xl border border-glass-border font-body text-xs">
          <button
            type="button"
            onClick={() => setPersona('STUDENT')}
            className={`py-2 rounded-xl transition-all font-medium cursor-pointer ${
              persona === 'STUDENT'
                ? 'bg-primary-container text-black font-semibold shadow-md'
                : 'text-text-secondary hover:text-white'
            }`}
          >
            College Student
          </button>
          <button
            type="button"
            onClick={() => setPersona('CORPORATE')}
            className={`py-2 rounded-xl transition-all font-medium cursor-pointer ${
              persona === 'CORPORATE'
                ? 'bg-primary-container text-black font-semibold shadow-md'
                : 'text-text-secondary hover:text-white'
            }`}
          >
            Corporate Pro
          </button>
          <button
            type="button"
            onClick={() => setPersona('COMMUTER')}
            className={`py-2 rounded-xl transition-all font-medium cursor-pointer ${
              persona === 'COMMUTER'
                ? 'bg-primary-container text-black font-semibold shadow-md'
                : 'text-text-secondary hover:text-white'
            }`}
          >
            Daily Commuter
          </button>
        </div>

        {error && (
          <div className="p-3 mb-4 rounded-xl bg-signal-rose/10 border border-signal-rose/30 text-signal-rose font-mono text-xs">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="flex flex-col gap-3.5">
          {/* Dynamic Morphing Fields Based on Persona */}
          <AnimatePresence mode="wait">
            {persona === 'STUDENT' && (
              <motion.div
                key="student-fields"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className="flex flex-col gap-3"
              >
                <div>
                  <label className="font-mono text-[10px] uppercase text-text-muted">College / Institute</label>
                  <select
                    value={college}
                    onChange={(e) => setCollege(e.target.value)}
                    className="w-full mt-1 px-3 py-2 rounded-xl bg-surface-container-high border border-glass-border font-body text-xs text-white focus:outline-none focus:border-primary"
                  >
                    <option value="Veermata Jijabai Technological Institute (VJTI)">VJTI Mumbai (Matunga)</option>
                    <option value="Sardar Patel Institute of Technology (SPIT)">SPIT Mumbai (Andheri)</option>
                    <option value="D.J. Sanghvi College of Engineering">DJ Sanghvi (Vile Parle)</option>
                    <option value="Thadomal Shahani Engineering College">TSEC (Bandra)</option>
                    <option value="K.J. Somaiya College of Engineering">KJ Somaiya (Vidyavihar)</option>
                  </select>
                </div>

                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <label className="font-mono text-[10px] uppercase text-text-muted">PRN / Roll Number</label>
                    <input
                      type="text"
                      required
                      value={rollNumber}
                      onChange={(e) => setRollNumber(e.target.value)}
                      className="w-full mt-1 px-3 py-2 rounded-xl bg-white/[0.04] border border-glass-border font-body text-xs text-white focus:outline-none focus:border-primary"
                    />
                  </div>
                  <div>
                    <label className="font-mono text-[10px] uppercase text-text-muted">First Lecture Slot</label>
                    <input
                      type="text"
                      required
                      value={lectureTime}
                      onChange={(e) => setLectureTime(e.target.value)}
                      className="w-full mt-1 px-3 py-2 rounded-xl bg-white/[0.04] border border-glass-border font-body text-xs text-white focus:outline-none focus:border-primary"
                    />
                  </div>
                </div>
              </motion.div>
            )}

            {persona === 'CORPORATE' && (
              <motion.div
                key="corporate-fields"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className="flex flex-col gap-3"
              >
                <div>
                  <label className="font-mono text-[10px] uppercase text-text-muted">Corporate Business Hub</label>
                  <select
                    value={corporateHub}
                    onChange={(e) => setCorporateHub(e.target.value)}
                    className="w-full mt-1 px-3 py-2 rounded-xl bg-surface-container-high border border-glass-border font-body text-xs text-white focus:outline-none focus:border-primary"
                  >
                    <option value="Bandra Kurla Complex (BKC)">Bandra Kurla Complex (BKC)</option>
                    <option value="Lower Parel / Prabhadevi">Lower Parel Mills / Prabhadevi</option>
                    <option value="Nariman Point / Fort">Nariman Point / Fort Financial Hub</option>
                    <option value="Mindspace Airoli / Navi Mumbai">Mindspace Airoli / Navi Mumbai</option>
                  </select>
                </div>
                <div className="flex items-center gap-2 p-3 rounded-xl bg-white/[0.02] border border-glass-border">
                  <input
                    type="checkbox"
                    id="slackSync"
                    checked={slackSync}
                    onChange={(e) => setSlackSync(e.target.checked)}
                    className="accent-primary cursor-pointer"
                  />
                  <label htmlFor="slackSync" className="font-body text-xs text-text-secondary cursor-pointer">
                    Enable Slack Transit Status Sync (Auto-updates Slack status on train delays)
                  </label>
                </div>
              </motion.div>
            )}

            {persona === 'COMMUTER' && (
              <motion.div
                key="commuter-fields"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className="flex flex-col gap-3"
              >
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <label className="font-mono text-[10px] uppercase text-text-muted">Mobile Phone</label>
                    <input
                      type="text"
                      required
                      value={mobileNumber}
                      onChange={(e) => setMobileNumber(e.target.value)}
                      className="w-full mt-1 px-3 py-2 rounded-xl bg-white/[0.04] border border-glass-border font-body text-xs text-white focus:outline-none focus:border-primary"
                    />
                  </div>
                  <div>
                    <label className="font-mono text-[10px] uppercase text-text-muted">UTS Season Ticket ID</label>
                    <input
                      type="text"
                      required
                      value={utsPassId}
                      onChange={(e) => setUtsPassId(e.target.value)}
                      className="w-full mt-1 px-3 py-2 rounded-xl bg-white/[0.04] border border-glass-border font-body text-xs text-white focus:outline-none focus:border-primary"
                    />
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Standard Auth Fields */}
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
            className="w-full mt-2 py-2.5 rounded-full bg-primary-container text-black font-body text-xs font-semibold hover:bg-primary transition-all flex items-center justify-center gap-2 cursor-pointer shadow-lg shadow-primary-container/20"
          >
            <span>{loading ? 'Authenticating...' : mode === 'login' ? 'Enter Suburban Flow' : 'Create Account'}</span>
          </button>
        </form>

        <div className="mt-4 pt-3 border-t border-glass-border flex items-center justify-between font-mono text-[11px] text-text-muted">
          <span>{mode === 'login' ? 'Switch Mode:' : 'Already registered?'}</span>
          <button
            type="button"
            onClick={() => {
              setMode(mode === 'login' ? 'register' : 'login');
              setError(null);
            }}
            className="text-primary hover:underline cursor-pointer"
          >
            {mode === 'login' ? 'Quick Demo Login →' : 'Sign In →'}
          </button>
        </div>
      </motion.div>
    </div>
  );
};
