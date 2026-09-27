import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import type { DelayTokenPayload } from '../../lib/services/telemetryService';

interface DelayCertificateModalProps {
  isOpen: boolean;
  onClose: () => void;
  tokenData: DelayTokenPayload;
}

export const DelayCertificateModal: React.FC<DelayCertificateModalProps> = ({
  isOpen,
  onClose,
  tokenData,
}) => {
  const [copied, setCopied] = useState(false);
  const [emailSent, setEmailSent] = useState(false);
  const [downloading, setDownloading] = useState(false);

  if (!isOpen) return null;

  const handleCopyLink = () => {
    navigator.clipboard.writeText(tokenData.verificationUrl);
    setCopied(true);
    setTimeout(() => setCopied(false), 3000);
  };

  const handleSendEmail = () => {
    setEmailSent(true);
    setTimeout(() => setEmailSent(false), 4000);
  };

  const handleDownloadPdf = () => {
    setDownloading(true);
    setTimeout(() => {
      setDownloading(false);
      // Trigger browser simulated download
      const element = document.createElement('a');
      const file = new Blob(
        [
          `CENTRAL RAILWAY - SUBURBAN TRAFFIC DELAY CERTIFICATE\n` +
            `Token: ${tokenData.tokenUuid}\n` +
            `SHA-256: ${tokenData.verificationSha256}\n` +
            `Student: ${tokenData.studentName} (${tokenData.rollNumber})\n` +
            `Institution: ${tokenData.collegeName}\n` +
            `Train Rake: ${tokenData.trainRakeId} (${tokenData.lineCorridor})\n` +
            `Verified Delay: ${tokenData.delayMinutes} Minutes\n` +
            `TMS Signal Failure: ${tokenData.tmsSignalFailurePoint}\n` +
            `Digital Signature: ${tokenData.digitalSignature}\n` +
            `Verification URL: ${tokenData.verificationUrl}\n`,
        ],
        { type: 'text/plain' }
      );
      element.href = URL.createObjectURL(file);
      element.download = `CR_Delay_Token_${tokenData.tokenUuid}.txt`;
      document.body.appendChild(element);
      element.click();
      document.body.removeChild(element);
    }, 800);
  };

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 20 }}
          transition={{ type: 'spring', damping: 25, stiffness: 300 }}
          className="relative w-full max-w-xl p-6 sm:p-8 rounded-3xl bg-surface-obsidian border border-glass-border shadow-2xl text-text-primary overflow-hidden"
        >
          {/* Header */}
          <div className="flex items-start justify-between pb-4 border-b border-glass-border">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-secondary/20 flex items-center justify-center text-secondary shrink-0">
                <span className="material-symbols-outlined text-[24px]">verified</span>
              </div>
              <div className="flex flex-col">
                <span className="font-mono text-[10px] uppercase text-secondary font-semibold tracking-wider">
                  Central Railway • Traffic Management System (TMS)
                </span>
                <h3 className="font-headline text-2xl text-text-primary">Suburban Transit Delay Certificate</h3>
              </div>
            </div>
            <button
              onClick={onClose}
              className="w-8 h-8 rounded-full bg-white/[0.04] hover:bg-white/[0.1] flex items-center justify-center text-text-muted hover:text-white transition-colors cursor-pointer"
            >
              <span className="material-symbols-outlined text-[18px]">close</span>
            </button>
          </div>

          {/* Certificate Body Container */}
          <div className="my-5 p-5 rounded-2xl bg-white/[0.02] border border-glass-border flex flex-col gap-3 font-mono text-xs">
            {/* Certificate Header Stamp */}
            <div className="flex items-center justify-between pb-3 border-b border-white/[0.06]">
              <div>
                <span className="text-text-muted text-[10px]">Certificate UUID:</span>
                <p className="text-text-primary font-bold">{tokenData.tokenUuid}</p>
              </div>
              <div className="text-right">
                <span className="text-text-muted text-[10px]">SHA-256 Digest:</span>
                <p className="text-primary font-bold text-[11px]">{tokenData.verificationSha256}</p>
              </div>
            </div>

            {/* Commuter / Student Metadata */}
            <div className="grid grid-cols-2 gap-3 py-1">
              <div>
                <span className="text-text-muted text-[10px] uppercase">Commuter / Student</span>
                <p className="text-text-primary font-semibold">{tokenData.studentName}</p>
                <p className="text-text-secondary text-[11px]">{tokenData.rollNumber} • {tokenData.collegeName}</p>
              </div>
              <div>
                <span className="text-text-muted text-[10px] uppercase">Tracked Rake & Line</span>
                <p className="text-text-primary font-semibold">{tokenData.trainRakeId}</p>
                <p className="text-secondary text-[11px]">Central Main Line (Down Through)</p>
              </div>
            </div>

            {/* Delay & TMS Failure Point */}
            <div className="p-3 rounded-xl bg-secondary/10 border border-secondary/20 flex flex-col gap-1">
              <div className="flex items-center justify-between">
                <span className="text-secondary font-bold text-xs uppercase">Verified Schedule Delay</span>
                <span className="text-secondary font-extrabold text-sm">+{tokenData.delayMinutes} Minutes</span>
              </div>
              <p className="text-text-secondary text-[11px] font-sans">
                <strong className="text-text-primary">TMS Failure Point:</strong> {tokenData.tmsSignalFailurePoint}
              </p>
              <p className="text-text-muted text-[10px] font-sans italic">
                "{tokenData.motormanRemarks}"
              </p>
            </div>

            {/* Digital Signature & Validity */}
            <div className="flex items-center justify-between pt-2 text-[10px] text-text-muted">
              <span>Issued: {tokenData.issuedAt} • Valid till: {tokenData.validUntil}</span>
              <span className="text-primary font-medium">{tokenData.digitalSignature}</span>
            </div>
          </div>

          {/* Interactive Action Buttons */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
            <button
              onClick={handleCopyLink}
              className="py-2.5 px-3 rounded-xl bg-white/[0.05] hover:bg-white/[0.1] text-text-primary font-body text-xs font-medium transition-all flex items-center justify-center gap-1.5 cursor-pointer border border-glass-border"
            >
              <span className="material-symbols-outlined text-[16px] text-primary">
                {copied ? 'check' : 'link'}
              </span>
              <span>{copied ? 'Copied URL!' : 'Copy Verified Link'}</span>
            </button>

            <button
              onClick={handleSendEmail}
              className="py-2.5 px-3 rounded-xl bg-white/[0.05] hover:bg-white/[0.1] text-text-primary font-body text-xs font-medium transition-all flex items-center justify-center gap-1.5 cursor-pointer border border-glass-border"
            >
              <span className="material-symbols-outlined text-[16px] text-secondary">
                {emailSent ? 'mark_email_read' : 'mail'}
              </span>
              <span>{emailSent ? 'Sent to HOD CS!' : 'Send to HOD Email'}</span>
            </button>

            <button
              onClick={handleDownloadPdf}
              className="py-2.5 px-3 rounded-xl bg-primary-container text-black font-body text-xs font-semibold hover:bg-primary transition-all flex items-center justify-center gap-1.5 cursor-pointer shadow-lg shadow-primary-container/20"
            >
              <span className="material-symbols-outlined text-[16px]">
                {downloading ? 'hourglass_top' : 'download'}
              </span>
              <span>{downloading ? 'Generating...' : 'Download PDF'}</span>
            </button>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
};
