import Image from 'next/image'
import { Camera, User } from 'lucide-react'
import type { ChangeEvent, RefObject } from 'react'

import { getProxiedImageUrl } from '@/lib/utils/image-proxy'

interface AvatarUploadFieldProps {
  fileInputRef: RefObject<HTMLInputElement | null>
  previewUrl: string
  currentImage?: string
  onPhotoChange: () => void
  onFileChange: (e: ChangeEvent<HTMLInputElement>) => void
}

const AvatarUploadField = ({
  fileInputRef,
  previewUrl,
  currentImage,
  onPhotoChange,
  onFileChange,
}: AvatarUploadFieldProps) => {
  return (
    <div className="flex items-center gap-5">
      <input
        type="file"
        id="image"
        ref={fileInputRef}
        onChange={onFileChange}
        className="hidden"
        accept="image/*"
      />

      <div className="relative flex size-20 shrink-0 cursor-pointer items-center justify-center overflow-hidden rounded-full bg-gray-100">
        {previewUrl || currentImage ? (
          <Image
            src={previewUrl || getProxiedImageUrl(currentImage)}
            alt="Фото профиля"
            fill
            sizes="80px"
            className="object-cover hover:cursor-pointer"
          />
        ) : (
          <User className="size-8 text-gray-400 hover:cursor-pointer" />
        )}

        <button
          type="button"
          onClick={onPhotoChange}
          aria-label="Изменить фотографию"
          className="absolute inset-0 flex cursor-pointer items-center justify-center bg-black/0 text-white opacity-0 transition-all hover:bg-black/40 hover:opacity-100"
        >
          <Camera className="size-5 cursor-pointer" />
        </button>
      </div>

      <div>
        <p className="text-sm font-medium text-gray-900">Изображение профиля</p>
        <p className="mt-1 text-xs text-gray-500">JPG или PNG, размер файла до 5 МБ.</p>
        <button
          type="button"
          onClick={onPhotoChange}
          className="mt-2 cursor-pointer text-sm font-medium text-orange-500 transition-colors hover:text-orange-600"
        >
          Изменить фото
        </button>
      </div>
    </div>
  )
}

export default AvatarUploadField
