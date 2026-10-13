/**
 * !Преобразует URL изображения с бекенда в проксированный URL через Next.js API route
 * !Это решает проблему с блокировкой приватных IP (127.0.0.1) в Next.js Image
 */
export function getProxiedImageUrl(backendUrl: string | null | undefined): string {
  if (!backendUrl) {
    return '/images/no-photo.png' // fallback изображение
  }

  if (backendUrl.startsWith('/uploads/')) {
    return `/api/media${backendUrl}`
  }

  if (
    backendUrl.startsWith('/') ||
    (!backendUrl.includes('127.0.0.1') && !backendUrl.includes('localhost'))
  ) {
    return backendUrl
  }

  try {
    const url = new URL(backendUrl)
    const path = url.pathname.startsWith('/uploads/')
      ? url.pathname.slice(1)
      : url.pathname.replace(/^\/media\//, '')
    return `/api/media/${path}`
  } catch (error) {
    console.error('Error parsing image URL:', error)
    return '/images/no-photo.png'
  }
}
