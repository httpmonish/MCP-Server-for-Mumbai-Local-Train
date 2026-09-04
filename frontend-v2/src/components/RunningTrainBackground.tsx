import React from "react";

export const RunningTrainBackground: React.FC = () => {
  return (
    <div className="tp-video-bg" aria-hidden="true">
      {/* Pure Mumbai Local video — no overlays, no grey layers */}
      <video
        autoPlay
        loop
        muted
        playsInline
        key="mumbai-local-bg"
        className="w-full h-full object-cover object-center"
      >
        <source src="/videos/mumbai_local_bg.mp4" type="video/mp4" />
      </video>
      {/* Subtle dark gradient overlay for text legibility only */}
      <div className="tp-video-overlay" />
    </div>
  );
};
