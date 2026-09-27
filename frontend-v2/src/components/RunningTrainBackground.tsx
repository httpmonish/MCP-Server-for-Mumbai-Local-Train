import React from "react";

export type VideoClipId = "station_1080" | "city_1080" | "mumbai_classic";

interface RunningTrainBackgroundProps {
  clipId?: VideoClipId;
  dimLevel?: number; // 0 to 100
}

const VIDEO_SOURCES: Record<VideoClipId, string> = {
  station_1080: "/videos/train_hd_1080.mp4",
  city_1080: "/videos/transit_city_1080.mp4",
  mumbai_classic: "/videos/mumbai_local_bg.mp4",
};

export const RunningTrainBackground: React.FC<RunningTrainBackgroundProps> = ({
  clipId = "station_1080",
  dimLevel = 25,
}) => {
  const currentSrc = VIDEO_SOURCES[clipId] || VIDEO_SOURCES.station_1080;

  return (
    <div className="fixed inset-0 w-full h-full overflow-hidden z-0 bg-slate-950" aria-hidden="true">
      <video
        key={currentSrc}
        autoPlay
        loop
        muted
        playsInline
        preload="auto"
        className="w-full h-full object-cover object-center transition-all duration-700 filter brightness-95 contrast-105"
      >
        <source src={currentSrc} type="video/mp4" />
      </video>

      {/* Subtle cinematic vignette for legibility */}
      {dimLevel > 0 && (
        <div
          className="absolute inset-0 bg-gradient-to-t from-black/70 via-black/20 to-black/35 pointer-events-none transition-opacity duration-500"
          style={{ opacity: dimLevel / 100 }}
        />
      )}
    </div>
  );
};
