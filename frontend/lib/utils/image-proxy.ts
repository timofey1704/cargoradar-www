/**
 * !Преобразует URL изображения с бекенда в проксированный URL через Next.js API route
 * !Это решает проблему с блокировкой приватных IP (127.0.0.1) в Next.js Image
 */
export function getProxiedImageUrl(backendUrl: string | null | undefined): string {
  if (!backendUrl) {
    return '/images/no-photo.png' // fallback изображение
  }

  // если это уже относительный URL или внешний URL (не локальный), возвращаем как есть
  if (
    backendUrl.startsWith('/') ||
    (!backendUrl.includes('127.0.0.1') && !backendUrl.includes('localhost'))
  ) {
    return backendUrl
  }

  try {
    const url = new URL(backendUrl)
    // извлекаем путь после /media/
    const mediaPath = url.pathname.replace('/media/', '')

    // возвращаем проксированный URL через API route
    return `/api/media/${mediaPath}`
  } catch (error) {
    console.error('Error parsing image URL:', error)
    return '/images/no-photo.png'
  }
}
