declare global {
  interface Window {
    Telegram: {
      WebApp: {
        initData: string
        initDataUnsafe: Record<string, unknown>
        ready: () => void
        close: () => void
        expand: () => void
        MainButton: {
          text: string
          show: () => void
          hide: () => void
          onClick: (cb: () => void) => void
          offClick: (cb: () => void) => void
        }
        BackButton: {
          show: () => void
          hide: () => void
          onClick: (cb: () => void) => void
          offClick: (cb: () => void) => void
        }
        themeParams: Record<string, string>
        colorScheme: 'light' | 'dark'
        onEvent: (event: string, cb: () => void) => void
        offEvent: (event: string, cb: () => void) => void
      }
    }
  }
}

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

async function request<T>(
  method: string,
  url: string,
  body?: unknown
): Promise<T> {
  const initData = window.Telegram?.WebApp?.initData ?? ''

  const headers: Record<string, string> = {
    'Authorization': `tma ${initData}`,
    'Content-Type': 'application/json',
  }

  const options: RequestInit = {
    method,
    headers,
  }

  if (body !== undefined) {
    options.body = JSON.stringify(body)
  }

  const response = await fetch(url, options)

  if (!response.ok) {
    let errorMessage = `HTTP ${response.status}`
    try {
      const errorBody = await response.json()
      if (errorBody.detail) {
        errorMessage = errorBody.detail
      } else if (errorBody.message) {
        errorMessage = errorBody.message
      }
    } catch {
      // если тело ответа не JSON, используем статус
    }
    throw new ApiError(response.status, errorMessage)
  }

  if (response.status === 204) {
    return undefined as T
  }

  return response.json()
}

export function get<T>(url: string): Promise<T> {
  return request<T>('GET', url)
}

export function post<T>(url: string, body?: unknown): Promise<T> {
  return request<T>('POST', url, body)
}

export function put<T>(url: string, body?: unknown): Promise<T> {
  return request<T>('PUT', url, body)
}

export function del<T>(url: string): Promise<T> {
  return request<T>('DELETE', url)
}
