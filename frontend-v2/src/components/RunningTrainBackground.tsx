import React from "react";

export const RunningTrainBackground: React.FC = () => {
  return (
    <div
      className="fixed inset-0 pointer-events-none overflow-hidden z-0 select-none"
      aria-hidden="true"
    >
      {/* PURE VIDEO BACKGROUND: No grey layers, no cartoon trains, no frames - ONLY the live Mumbai Local footage */}
      <video
        autoPlay
        loop
        muted
        playsInline
        key="mumbai-local-clean-video"
        className="w-full h-full object-cover object-center"
      >
        <source src="/videos/mumbai_local_bg.mp4" type="video/mp4" />
      </video>
    </div>
  );
};
