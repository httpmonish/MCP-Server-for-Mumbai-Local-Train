import { CONFIG } from './config.js';

async function fetchWithTimeout(endpoint, options = {}, timeoutMs = CONFIG.REQUEST_TIMEOUT_MS) {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const response = await fetch(`${CONFIG.API_BASE_URL}${endpoint}`, {
      ...options,
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    if (response.status === 429) {
      throw new Error("Rate limit exceeded (10 req/min). Please wait before trying again.");
    }

    if (response.status === 401) {
      throw new Error("Authentication failed. Check your portal username and password.");
    }

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP Error: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    if (error.name === 'AbortError') {
      throw new Error("Request timed out. Downstream server took too long.");
    }
    throw error;
  }
}

export async function apiGetAttendance(studentId, credentials) {
  return fetchWithTimeout(`/api/v1/academic/attendance/${studentId}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(credentials),
  });
}

export async function apiGetExams(studentId, credentials) {
  return fetchWithTimeout(`/api/v1/academic/exams/${studentId}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(credentials),
  });
}

export async function apiGetNextTrains(fromStation, toStation) {
  return fetchWithTimeout(`/api/v1/trains/next?from_station=${encodeURIComponent(fromStation)}&to_station=${encodeURIComponent(toStation)}&limit=4`);
}

export async function apiCheckHealth() {
  return fetchWithTimeout('/health');
}
