import React, { useState } from 'react';
import { motion } from 'framer-motion';
import type { CorridorId } from '../lib/services/telemetryService';
import { UserProfilePopover } from './modals/UserProfilePopover';
import type { PersonaType } from './modals/UserProfilePopover';

interface HeaderProps {
  activeLine: CorridorId;
  onSelectLine: (line: CorridorId) => void;
  user: {
    name: string;
    org: string;
    role?: string;
    prn?: string;
    semester?: string;
    utsPassId?: string;
  } | null;
  currentPersona: PersonaType;
  onSelectPersona: (persona: PersonaType) => void;
  onOpenAuth: () => void;
  onOpenEditProfile: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  activeLine,
  onSelectLine,
  user,
  currentPersona,
  onSelectPersona,
  onOpenAuth,
  onOpenEditProfile,
}) => {
  const [profileOpen, setProfileOpen] = useState(false);

  const lines: { id: CorridorId; label: string }[] = [
    { id: 'central-main', label: 'Central Main' },
    { id: 'western-line', label: 'Western Line' },
    { id: 'harbour', label: 'Harbour' },
    { id: 'trans-harbour', label: 'Trans-Harbour' },
  ];

  return (
    <header className="fixed top-0 w-full z-40 bg-surface-obsidian/85 backdrop-blur-2xl border-b border-glass-border">
      <div className="h-20 w-full px-4 sm:px-6 max-w-[1440px] mx-auto flex items-center justify-between gap-4">
        {/* Brand */}
        <div className="flex items-center gap-3 shrink-0 cursor-pointer">
          <div className="flex flex-col">
            <div className="flex items-baseline gap-1.5">
              <span className="font-headline text-2xl tracking-tight text-text-primary">
                मुंबई<span className="font-body text-base font-semibold text-primary tracking-normal">Teleport</span>
              </span>
            </div>
            <span className="font-mono text-[10px] uppercase text-text-muted tracking-widest">
              Suburban Flow Telemetry
            </span>
          </div>
        </div>

        {/* Corridor Line Tabs with Framer Motion Sliding Highlight */}
        <div className="hidden lg:flex items-center justify-center flex-1 max-w-2xl px-3">
          <nav className="flex items-center gap-1 p-1 bg-white/[0.04] backdrop-blur-2xl rounded-full border border-glass-border relative">
            {lines.map((line) => {
              const isActive = activeLine === line.id;
              return (
                <button
                  key={line.id}
                  onClick={() => onSelectLine(line.id)}
                  className={`relative px-4 py-1.5 rounded-full text-xs font-body transition-colors whitespace-nowrap cursor-pointer z-10 ${
                    isActive ? 'text-black font-semibold' : 'text-text-secondary hover:text-text-primary'
                  }`}
                >
                  {isActive && (
                    <motion.div
                      layoutId="corridorHighlight"
                      className="absolute inset-0 bg-primary-container rounded-full shadow-[0_0_20px_rgba(16,185,129,0.4)] -z-10"
                      transition={{ type: 'spring', damping: 26, stiffness: 350 }}
                    />
                  )}
                  {line.label}
                </button>
              );
            })}
          </nav>
        </div>

        {/* Status & Commuter Identity Avatar */}
        <div className="flex items-center gap-3 shrink-0">
          <div className="hidden sm:flex items-center gap-2.5 px-3 py-1.5 rounded-full bg-white/[0.03] backdrop-blur-xl border border-glass-border">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary-container opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-primary-container shadow-[0_0_8px_rgba(16,185,129,0.9)]"></span>
            </span>
            <span className="font-mono text-[11px] text-text-secondary tracking-wider">
              CR/WR SYNCED <span className="text-text-muted">•</span> HEADWAY 3m 40s
            </span>
          </div>

          {/* Commuter Avatar Button */}
          <div className="relative">
            <button
              onClick={() => {
                if (!user) {
                  onOpenAuth();
                } else {
                  setProfileOpen((prev) => !prev);
                }
              }}
              className="flex items-center gap-2 pl-1.5 pr-3 py-1 rounded-full bg-white/[0.03] backdrop-blur-xl border border-glass-border hover:bg-white/[0.06] hover:border-primary/40 transition-all cursor-pointer"
            >
              <div className="w-7 h-7 rounded-full bg-primary flex items-center justify-center shrink-0 text-black font-bold text-xs">
                {user?.name?.[0] || 'A'}
              </div>
              <div className="hidden md:flex flex-col text-left">
                <span className="font-body text-xs text-text-primary leading-tight font-medium">
                  {user ? user.name : 'Aditya'}
                </span>
                <span className="font-mono text-[9px] text-primary leading-tight font-medium">
                  {currentPersona === 'STUDENT'
                    ? user?.semester || 'VJTI Sem VI'
                    : currentPersona === 'CORPORATE'
                    ? 'Corporate Pro • BKC'
                    : 'Daily Commuter'}
                </span>
              </div>
              <span className="material-symbols-outlined text-text-muted text-[16px]">expand_more</span>
            </button>

            {/* Profile Popover */}
            <UserProfilePopover
              isOpen={profileOpen}
              onClose={() => setProfileOpen(false)}
              currentPersona={currentPersona}
              onSelectPersona={onSelectPersona}
              user={user}
              onOpenEditProfile={() => {
                onOpenEditProfile();
                setProfileOpen(false);
              }}
            />
          </div>
        </div>
      </div>
    </header>
  );
};
