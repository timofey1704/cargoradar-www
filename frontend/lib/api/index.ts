// frontend/lib/api/index.ts
// Общая fetch-обёртка для всех запросов к бэкенду.
//
// Что делает:
//   - ходит с credentials: 'include' (httpOnly-куки — основной способ аутентификации);
//   - сериализует тело в JSON и проставляет Content-Type;
//   - при 401 один раз перевыпускает пару токенов по refresh-куке и повторяет запрос.
//     JS не видит httpOnly refresh-куку, поэтому бэкенд сам берёт её из cookie
//     на POST /client/auth/refresh и /executor/auth/refresh (см. backend).

type ApiRole = 'client' | 'executor'

export type HttpMethod = 'GET' | 'POST' | 'PATCH' | 'PUT' | 'DELETE'

export interface ApiRequestOptions {
  method?: HttpMethod
  /** Передаётся в JSON-теле. `undefined`/опущен — тело не отправляем. */
  body?: unknown
  headers?: Record<string, string>
  signal?: AbortSignal
  /** Перевыпускать токены при 401 и пробовать ещё раз. По умолчанию true. */
  retryOnUnauthorized?: boolean
}

export class ApiError extends Error {
  readonly status: number

  constructor(status: number, message: string) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

const REFRESH_URLS: Record<ApiRole, string> = {
  client: `${process.env.NEXT_PUBLIC_API_URL}/client/auth/refresh`,
  executor: `${process.env.NEXT_PUBLIC_API_URL}/executor/auth/refresh`,
}

function roleForPath(path: string): ApiRole {
  return path.startsWith('/executor') ? 'executor' : 'client'
}

async function refreshSession(role: ApiRole): Promise<boolean> {
  try {
    const response = await fetch(REFRESH_URLS[role], {
      method: 'POST',
      credentials: 'include',
    })

    return response.ok
  } catch {
    return false
  }
}

async function errorMessage(response: Response): Promise<string> {
  try {
    const data = await response.json()
    if (data && typeof data.detail === 'string') {
      return data.detail
    }
  } catch {
    // ответ не JSON — оставляем статус в сообщении ниже
  }

  return `Request failed with status ${response.status}`
}

/**
 * Общая fetch-обёртка:
 * принимает путь без базового URL (например, `/client/auth/me`).
 */
export async function apiRequest<T = unknown>(
  path: string,
  { method = 'GET', body, headers = {}, retryOnUnauthorized = true, signal }: ApiRequestOptions = {}
): Promise<T> {
  const url = `${process.env.NEXT_PUBLIC_API_URL}${path}`

  const send = () =>
    fetch(url, {
      method,
      credentials: 'include',
      headers: {
        ...(body !== undefined && !(body instanceof FormData)
          ? { 'Content-Type': 'application/json' }
          : undefined),
        ...headers,
      },
      body:
        body !== undefined ? (body instanceof FormData ? body : JSON.stringify(body)) : undefined,
      signal,
    })

  let response = await send()

  // Access-токен живёт недолго (30 минут), а на странице мог уже истечь.
  // Один раз пробуем обновить пару токенов и повторить исходный запрос.
  if (retryOnUnauthorized && response.status === 401) {
    const isRefreshed = await refreshSession(roleForPath(path))
    if (isRefreshed) {
      response = await send()
    }
  }

  if (response.status === 401) {
    throw new ApiError(401, 'UNAUTHORIZED')
  }

  if (!response.ok) {
    throw new ApiError(response.status, await errorMessage(response))
  }

  if (response.status === 204) {
    return undefined as T
  }

  return (await response.json()) as T
}
