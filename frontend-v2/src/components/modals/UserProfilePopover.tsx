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
}

export const UserProfilePopover: React.FC<UserProfilePopoverProps> = ({
  isOpen,
  onClose,
  currentPersona,
  onSelectPersona,
  user,
  onOpenEditProfile,
}) => {
  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex items-start justify-end p-4 pt-20 bg-black/40 backdrop-blur-xs" onClick={onClose}>
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: -10 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: -10 }}
          transition={{ type: 'spring', damping: 25, stiffness: 350 }}
          onClick={(e) => e.stopPropagation()}
          className="relative w-full max-w-sm p-5 rounded-3xl bg-surface-obsidian/95 border border-glass-border shadow-2xl text-text-primary backdrop-blur-2xl"
        >
          {/* User Info Header */}
          <div className="flex items-center gap-3 pb-3 border-b border-glass-border">
            <div className="w-12 h-12 rounded-full bg-primary flex items-center justify-center text-black font-bold text-lg shrink-0">
              {user?.name?.[0] || 'A'}
            </div>
            <div className="flex flex-col">
              <span className="font-headline text-lg text-text-primary leading-tight font-medium">
                {user?.name || 'Aditya Sharma'}
              </span>
              <span className="font-mono text-xs text-primary font-medium">
                {user?.prn || 'PRN: 211080042'}
              </span>
              <span className="font-mono text-[10px] text-text-muted">
                {user?.org || 'Veermata Jijabai Technological Institute (VJTI)'}
              </span>
            </div>
          </div>

          {/* Academic / Persona Snapshot */}
          <div className="my-3 p-3 rounded-2xl bg-white/[0.03] border border-glass-border flex flex-col gap-1.5 font-mono text-xs">
            <div className="flex items-center justify-between">
              <span className="text-text-muted">Department / Sem:</span>
              <span className="text-text-primary font-semibold">{user?.semester || 'Sem VI • B.Tech CS'}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-text-muted">Season Ticket:</span>
              <span className="text-primary font-medium">{user?.utsPassId || 'UTS-II-CR-98401'} (Exp: Oct 2026)</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-text-muted">Attendance Status:</span>
              <span className="text-secondary font-semibold">75.4% (Threshold 75%)</span>
            </div>
          </div>

          {/* Persona Switcher Tabs */}
          <div className="flex flex-col gap-1.5 py-1">
            <span className="font-mono text-[10px] uppercase text-text-muted tracking-wider">
              Switch Persona Mode
            </span>
            <div className="grid grid-cols-3 gap-1 p-1 bg-white/[0.04] rounded-2xl border border-glass-border font-body text-xs">
              <button
                onClick={() => onSelectPersona('STUDENT')}
                className={`py-1.5 rounded-xl transition-all font-medium ${
                  currentPersona === 'STUDENT'
                    ? 'bg-primary-container text-black font-semibold shadow-md'
                    : 'text-text-secondary hover:text-white'
                }`}
              >
                Student
              </button>
              <button
                onClick={() => onSelectPersona('CORPORATE')}
                className={`py-1.5 rounded-xl transition-all font-medium ${
                  currentPersona === 'CORPORATE'
                    ? 'bg-primary-container text-black font-semibold shadow-md'
                    : 'text-text-secondary hover:text-white'
                }`}
              >
                Corporate
              </button>
              <button
                onClick={() => onSelectPersona('COMMUTER')}
                className={`py-1.5 rounded-xl transition-all font-medium ${
                  currentPersona === 'COMMUTER'
                    ? 'bg-primary-container text-black font-semibold shadow-md'
                    : 'text-text-secondary hover:text-white'
                }`}
              >
                Commuter
              </button>
            </div>
          </div>

          {/* Actions */}
          <div className="mt-4 pt-3 border-t border-glass-border flex items-center justify-between">
            <button
              onClick={() => {
                onOpenEditProfile();
                onClose();
              }}
              className="font-mono text-xs text-primary hover:underline cursor-pointer flex items-center gap-1"
            >
              <span className="material-symbols-outlined text-[14px]">edit</span>
              Edit Academic Profile
            </button>
            <button
              onClick={onClose}
              className="px-3.5 py-1.5 rounded-full bg-white/[0.06] hover:bg-white/[0.12] text-text-primary font-mono text-xs transition-colors cursor-pointer"
            >
              Close
            </button>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
};
