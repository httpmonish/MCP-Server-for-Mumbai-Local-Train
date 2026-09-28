import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

import type { PersonaType } from './UserProfilePopover';

interface PedestrianSprintModalProps {
  isOpen: boolean;
  onClose: () => void;
  trainArrivalTime?: string;
  lectureStartTime?: string;
  persona?: PersonaType;
}

export const PedestrianSprintModal: React.FC<PedestrianSprintModalProps> = ({
  isOpen,
  onClose,
  trainArrivalTime = '09:23 AM',
  lectureStartTime = '09:30 AM',
  persona = 'COMMUTER',
}) => {
  const [secondsRemaining, setSecondsRemaining] = useState(420); // 7 minutes

  useEffect(() => {
    if (!isOpen) return;
    const timer = setInterval(() => {
      setSecondsRemaining((prev) => (prev > 0 ? prev - 1 : 0));
    }, 1000);
    return () => clearInterval(timer);
  }, [isOpen]);

  const mins = Math.floor(secondsRemaining / 60);
  const secs = secondsRemaining % 60;

  return (
    <AnimatePresence>
      {isOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            transition={{ type: 'spring', damping: 25, stiffness: 300 }}
            className="relative w-full max-w-lg p-6 rounded-3xl bg-surface-obsidian border border-glass-border shadow-2xl text-text-primary overflow-hidden"
          >
            {/* Ambient Backlight */}
            <div className="absolute -right-20 -top-20 w-60 h-60 rounded-full bg-primary/20 blur-3xl pointer-events-none"></div>

            {/* Header */}
            <div className="flex items-center justify-between pb-4 border-b border-glass-border">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center text-primary">
                  <span className="material-symbols-outlined text-[20px]">directions_walk</span>
                </div>
                <div className="flex flex-col">
                  <span className="font-mono text-[10px] uppercase text-primary font-semibold tracking-wider">
                    Contingency Protocol A
                  </span>
                  <h3 className="font-headline text-xl text-text-primary">
                    {persona === 'STUDENT'
                      ? 'Sprint Path: Matunga E. → VJTI'
                      : 'Express Egress & Rapid Transit Transfer'}
                  </h3>
                </div>
              </div>
              <button
                onClick={onClose}
                className="w-8 h-8 rounded-full bg-white/[0.04] hover:bg-white/[0.1] flex items-center justify-center text-text-muted hover:text-white transition-colors cursor-pointer"
              >
                <span className="material-symbols-outlined text-[18px]">close</span>
              </button>
            </div>

            {/* Countdown Banner */}
            <div className="my-4 p-4 rounded-2xl bg-white/[0.03] border border-glass-border flex items-center justify-between">
              <div className="flex flex-col">
                <span className="font-mono text-[10px] text-text-muted uppercase">Target Walking Window</span>
                <span className="font-mono text-2xl text-primary font-bold">
                  {mins}:{secs < 10 ? `0${secs}` : secs} <span className="text-xs font-normal text-text-secondary">remaining</span>
                </span>
              </div>
              <div className="flex flex-col text-right">
                <span className="font-mono text-[10px] text-text-muted">
                  {persona === 'STUDENT' ? 'Dadar Arr → Lecture' : 'Train Arr → Destination'}
                </span>
                <span className="font-mono text-xs text-text-primary">
                  {trainArrivalTime} → <span className="text-tertiary">{lectureStartTime}</span>
                </span>
              </div>
            </div>

            {/* Step by Step Pedestrian Turn Vector */}
            <div className="flex flex-col gap-3 py-2">
              <div className="flex items-start gap-3">
                <div className="w-6 h-6 rounded-full bg-primary/20 text-primary flex items-center justify-center font-mono text-xs font-bold shrink-0 mt-0.5">
                  1
                </div>
                <div className="flex flex-col">
                  <span className="font-body text-xs text-text-primary font-medium">
                    {persona === 'STUDENT' ? 'De-board Matunga Station PF 1' : 'De-board Rake at Optimal Platform Exit'}
                  </span>
                  <span className="font-body text-[11px] text-text-muted">
                    {persona === 'STUDENT'
                      ? 'Take Kalyan-end Foot Over Bridge towards East ticket counter.'
                      : 'Utilize mid-train Foot Over Bridge (FOB) for fast platform clearance.'}
                  </span>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <div className="w-6 h-6 rounded-full bg-primary/20 text-primary flex items-center justify-center font-mono text-xs font-bold shrink-0 mt-0.5">
                  2
                </div>
                <div className="flex flex-col">
                  <span className="font-body text-xs text-text-primary font-medium">
                    {persona === 'STUDENT' ? 'Exit to Dr. B.A. Road & Five Gardens' : 'Concourse Ingress / Station Egress'}
                  </span>
                  <span className="font-body text-[11px] text-text-muted">
                    {persona === 'STUDENT'
                      ? 'Cross signal at Maheshwari Udyan (2 mins walk).'
                      : 'Scan automatic fare collection gates or proceed through main exit concourse.'}
                  </span>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <div className="w-6 h-6 rounded-full bg-primary/20 text-primary flex items-center justify-center font-mono text-xs font-bold shrink-0 mt-0.5">
                  3
                </div>
                <div className="flex flex-col">
                  <span className="font-body text-xs text-text-primary font-medium">
                    {persona === 'STUDENT'
                      ? 'Enter VJTI Mechanical Building Gate #3'
                      : 'Arrive at Target Destination Hub'}
                  </span>
                  <span className="font-body text-[11px] text-text-muted">
                    {persona === 'STUDENT'
                      ? 'Biometric Machine #04 is located on Ground Floor Quadrangle.'
                      : 'On-schedule arrival completed within optimal buffer time.'}
                  </span>
                </div>
              </div>
            </div>

            {/* CTA */}
            <div className="mt-4 pt-3 border-t border-glass-border flex items-center justify-between">
              <span className="font-mono text-[10px] text-primary flex items-center gap-1">
                <span className="w-2 h-2 rounded-full bg-primary animate-ping"></span>
                Live GPS Radar Connected
              </span>
              <button
                onClick={onClose}
                className="px-5 py-2 rounded-full bg-primary-container text-black font-body text-xs font-semibold hover:bg-primary transition-all cursor-pointer"
              >
                Acknowledge & Begin Sprint
              </button>
            </div>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
};
