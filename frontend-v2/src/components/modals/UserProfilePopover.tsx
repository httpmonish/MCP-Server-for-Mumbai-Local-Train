import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';

export type PersonaType = 'STUDENT' | 'CORPORATE' | 'COMMUTER';

interface UserProfilePopoverProps {
  isOpen: boolean;
  onClose: () => void;
  currentPersona: PersonaType;
  onSelectPersona: (persona: PersonaType) => void;
  user: {
    name: string;
    org: string;
    role?: string;
    prn?: string;
    semester?: string;
    utsPassId?: string;
  } | null;
  onOpenEditProfile: () => void;
  onLogout: () => void;
}

export const UserProfilePopover: React.FC<UserProfilePopoverProps> = ({
  isOpen,
  onClose,
  currentPersona,
  onSelectPersona,
  user,
  onOpenEditProfile,
  onLogout,
}) => {
  if (!isOpen) return null;

  return (
    <AnimatePresence>
      {/* Backdrop */}
      <div
        className="fixed inset-0 z-50 flex items-start justify-end p-4 pt-20 bg-black/50 backdrop-blur-xs"
        onClick={onClose}
      >
        {/* Floating Card Popover */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: -10 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: -10 }}
          transition={{ type: 'spring', damping: 25, stiffness: 350 }}
          onClick={(e) => e.stopPropagation()}
          className="relative w-full max-w-sm p-5 rounded-3xl bg-surface-obsidian border border-glass-border shadow-2xl text-text-primary backdrop-blur-2xl flex flex-col gap-3 mr-2 sm:mr-6"
        >
          {/* User Header */}
          <div className="flex items-center justify-between pb-3 border-b border-glass-border">
            <div className="flex items-center gap-3">
              <div className="w-11 h-11 rounded-full bg-primary flex items-center justify-center text-black font-bold text-base shrink-0 shadow-[0_0_12px_rgba(78,222,163,0.4)]">
                {user ? user.name[0] : 'C'}
              </div>
              <div className="flex flex-col">
                <span className="font-headline text-base text-text-primary leading-tight font-medium">
                  {user ? user.name : 'Commuter Mode'}
                </span>
                <span className="font-mono text-xs text-primary font-medium">
                  {user ? user.prn || 'Verified Commuter' : 'Guest Passenger'}
                </span>
                <span className="font-mono text-[10px] text-text-muted truncate max-w-[200px]">
                  {user ? user.org : 'Mumbai Suburban Network'}
                </span>
              </div>
            </div>
            <button
              onClick={onClose}
              className="w-7 h-7 rounded-full bg-white/[0.04] hover:bg-white/[0.1] text-text-muted hover:text-white flex items-center justify-center transition-colors cursor-pointer"
            >
              <span className="material-symbols-outlined text-[16px]">close</span>
            </button>
          </div>

          {/* Account Snapshot / Commuter Status */}
          <div className="p-3 rounded-2xl bg-white/[0.03] border border-glass-border flex flex-col gap-1.5 font-mono text-xs">
            {user ? (
              <>
                <div className="flex items-center justify-between">
                  <span className="text-text-muted">Account Persona:</span>
                  <span className="text-text-primary font-semibold">{currentPersona}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-text-muted">Pass / Ticket ID:</span>
                  <span className="text-primary font-medium">{user.utsPassId || 'UTS-II-CR-98401'}</span>
                </div>
                {currentPersona === 'STUDENT' && (
                  <div className="flex items-center justify-between">
                    <span className="text-text-muted">Attendance Radar:</span>
                    <span className="text-primary font-semibold">75.4% (Active Safe)</span>
                  </div>
                )}
              </>
            ) : (
              <div className="flex flex-col gap-1">
                <span className="text-text-secondary text-[11px] font-sans">
                  You are viewing live suburban telemetry in open commuter mode.
                </span>
                <span className="text-primary text-[10px]">
                  Sign in to sync academic attendance or corporate work shifts.
                </span>
              </div>
            )}
          </div>

          {/* Persona Switcher Tabs */}
          <div className="flex flex-col gap-1.5 pt-1">
            <span className="font-mono text-[10px] uppercase text-text-muted tracking-wider">
              Switch Persona Mode
            </span>
            <div className="grid grid-cols-3 gap-1 p-1 bg-white/[0.04] rounded-2xl border border-glass-border font-body text-xs">
              <button
                onClick={() => onSelectPersona('COMMUTER')}
                className={`py-1.5 rounded-xl transition-all font-medium cursor-pointer ${
                  currentPersona === 'COMMUTER'
                    ? 'bg-primary-container text-black font-semibold shadow-md'
                    : 'text-text-secondary hover:text-white'
                }`}
              >
                Commuter
              </button>
              <button
                onClick={() => onSelectPersona('STUDENT')}
                className={`py-1.5 rounded-xl transition-all font-medium cursor-pointer ${
                  currentPersona === 'STUDENT'
                    ? 'bg-primary-container text-black font-semibold shadow-md'
                    : 'text-text-secondary hover:text-white'
                }`}
              >
                Student
              </button>
              <button
                onClick={() => onSelectPersona('CORPORATE')}
                className={`py-1.5 rounded-xl transition-all font-medium cursor-pointer ${
                  currentPersona === 'CORPORATE'
                    ? 'bg-primary-container text-black font-semibold shadow-md'
                    : 'text-text-secondary hover:text-white'
                }`}
              >
                Corporate
              </button>
            </div>
          </div>

          {/* Action Buttons: Sign In / Logout / Edit */}
          <div className="mt-2 pt-3 border-t border-glass-border flex items-center justify-between gap-2">
            {user ? (
              <>
                <button
                  onClick={() => {
                    onOpenEditProfile();
                    onClose();
                  }}
                  className="font-mono text-xs text-primary hover:underline cursor-pointer flex items-center gap-1"
                >
                  <span className="material-symbols-outlined text-[14px]">edit</span>
                  Edit Profile
                </button>
                <button
                  onClick={() => {
                    onLogout();
                    onClose();
                  }}
                  className="px-3.5 py-1.5 rounded-full bg-signal-rose/10 hover:bg-signal-rose/20 text-signal-rose border border-signal-rose/30 font-mono text-xs font-semibold transition-colors cursor-pointer flex items-center gap-1"
                >
                  <span className="material-symbols-outlined text-[14px]">logout</span>
                  Logout
                </button>
              </>
            ) : (
              <button
                onClick={() => {
                  onOpenEditProfile();
                  onClose();
                }}
                className="w-full py-2 rounded-full bg-primary-container text-black font-body text-xs font-semibold hover:bg-primary transition-all flex items-center justify-center gap-1.5 cursor-pointer shadow-md"
              >
                <span className="material-symbols-outlined text-[16px]">login</span>
                Sign In / Connect Profile
              </button>
            )}
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
};
