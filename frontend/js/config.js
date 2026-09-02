// Runtime environment detection
const isLocalhost = Boolean(
  window.location.hostname === "localhost" ||
  window.location.hostname === "127.0.0.1" ||
  window.location.hostname.endsWith(".local")
);

// Read override from window injection or fallback to deployed backend
const DEPLOYED_BACKEND_URL = "https://your-production-railway.railway.app";

export const CONFIG = {
  API_BASE_URL: isLocalhost ? "http://localhost:8000" : (window.ENV_API_URL || DEPLOYED_BACKEND_URL),
  REQUEST_TIMEOUT_MS: 15000,
  TRAIN_POLL_INTERVAL_MS: 60000,
  DEFAULT_FROM_STATION: "Thane",
  DEFAULT_TO_STATION: "Byculla"
};
