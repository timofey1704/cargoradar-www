import { useCallback, useRef, useState } from 'react'
import type { ChangeEvent } from 'react'

import { uploadImage } from '@/lib/utils/image-upload'
import { getProxiedImageUrl } from '@/lib/utils/image-proxy'
import showToast from '@/components/ui/toast'
import type { ProfileImageResponse } from '@/types/account'

interface UseProfileImageUploadParams {
  endpoint: string
  currentImage?: string
  onUploaded: (image: string) => void
}

export function useProfileImageUpload({
  endpoint,
  currentImage,
  onUploaded,
}: UseProfileImageUploadParams) {
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [previewUrl, setPreviewUrl] = useState<string>(getProxiedImageUrl(currentImage) || '')

  const handlePhotoChange = () => fileInputRef.current?.click()

  const handleFileChange = useCallback(
    async (e: ChangeEvent<HTMLInputElement>) => {
      const files = e.target.files
      if (!files || files.length === 0) return

      try {
        const file = files[0]
        if (!file.type.startsWith('image/')) {
          showToast({ type: 'error', message: 'Пожалуйста, выберите изображение' })
          return
        }

        setPreviewUrl(URL.createObjectURL(file))

        const response = await uploadImage<ProfileImageResponse>(file, endpoint)

        if (response.user?.image) {
          setPreviewUrl(getProxiedImageUrl(response.user.image))
          onUploaded(response.user.image)
        }

        showToast({ type: 'success', message: 'Фотография успешно обновлена' })
        e.target.value = ''
      } catch (error) {
        showToast({ type: 'error', message: 'Ошибка при загрузке фотографии' })
        console.error('Error handling file:', error)
      }
    },
    [endpoint, onUploaded]
  )

  return { fileInputRef, previewUrl, handlePhotoChange, handleFileChange }
}
