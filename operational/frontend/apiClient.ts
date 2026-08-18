export type ApiError = {
  message: string;
  status: number;
};

/**
 * Single browser-to-backend boundary for IntelliHire.
 *
 * All application API calls should use this client. Keeping the API base
 * same-origin preserves Google auth cookies and prevents exposing provider
 * credentials or internal backend URLs to the browser.
 */
export async function apiRequest<T>(
  path: string,
  init: RequestInit = {},
): Promise<T> {
  const normalized = path.startsWith('/') ? path : `/${path}`;
  const response = await fetch(normalized, {
    ...init,
    credentials: 'include',
    headers: {
      Accept: 'application/json',
      ...(init.body && !(init.body instanceof FormData)
        ? { 'Content-Type': 'application/json' }
        : {}),
      ...(init.headers || {}),
    },
  });

  if (!response.ok) {
    let message = `Request failed (${response.status})`;
    try {
      const body = await response.json();
      if (body?.message || body?.error) message = body.message || body.error;
    } catch {
      // Keep the HTTP status message when the backend returned non-JSON data.
    }
    const error: ApiError = { message, status: response.status };
    throw error;
  }

  return response.json() as Promise<T>;
}

export const api = {
  authMe: () => apiRequest<{ user?: { name?: string; email?: string; role?: string } }>('/api/auth/me'),
  aiGenerate: <T = unknown>(payload: unknown) =>
    apiRequest<T>('/api/ai/generate', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
};
