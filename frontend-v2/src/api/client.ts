const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export class ApiError extends Error {
  public status: number;
  public detail: string;

  constructor(status: number, message: string, detail: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.detail = detail;
  }
}

export async function apiClient<T>(
  endpoint: string,
  options: RequestInit = {},
  timeoutMs = 15000
): Promise<T> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const response = await fetch(`${BASE_URL}${endpoint}`, {
      ...options,
      signal: controller.signal,
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
        ...options.headers,
      },
    });

    if (!response.ok) {
      const errorPayload = await response.json().catch(() => ({}));
      const detail = errorPayload.detail || errorPayload.error || response.statusText;

      if (response.status === 429) {
        throw new ApiError(429, "Rate limit exceeded", "Too many requests. Please wait 60 seconds.");
      }
      if (response.status === 401) {
        throw new ApiError(401, "Authentication failed", "Invalid college portal username or password.");
      }
      throw new ApiError(response.status, "Server error", detail);
    }

    return (await response.json()) as T;
  } catch (error: any) {
    if (error.name === "AbortError") {
      throw new ApiError(408, "Request timed out", "Upstream server took too long to respond.");
    }
    throw error;
  } finally {
    clearTimeout(timeoutId);
  }
}
