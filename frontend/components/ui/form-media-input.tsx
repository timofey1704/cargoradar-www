'use client'

import Image from 'next/image'
import { ImagePlus, X } from 'lucide-react'
import { useEffect, useRef, useState } from 'react'
import { useFormContext } from 'react-hook-form'
import type { FieldValues, Path } from 'react-hook-form'

const EMPTY_FILES: File[] = []

interface FormMediaInputProps<T extends FieldValues> {
  name: Path<T>
  label?: string
  accept?: string
}

function FormMediaInput<T extends FieldValues>({
  name,
  label,
  accept = 'image/*',
}: FormMediaInputProps<T>) {
  const inputRef = useRef<HTMLInputElement>(null)
  const previewUrlsRef = useRef<string[]>([])
  const [previewUrls, setPreviewUrls] = useState<string[]>([])
  const {
    watch,
    setValue,
    formState: { errors },
  } = useFormContext<T>()
  const files = (watch(name) as File[] | undefined) ?? EMPTY_FILES
  const error = errors[name]?.message
  const hasError = Boolean(error)

  useEffect(() => {
    return () => previewUrlsRef.current.forEach(URL.revokeObjectURL)
  }, [])

  useEffect(() => {
    if (files.length === 0 && previewUrlsRef.current.length > 0) {
      previewUrlsRef.current.forEach(URL.revokeObjectURL)
      previewUrlsRef.current = []
    }
  }, [files])

  const replacePreviews = (nextFiles: File[]) => {
    const nextUrls = nextFiles.map(file => URL.createObjectURL(file))
    previewUrlsRef.current.forEach(URL.revokeObjectURL)
    previewUrlsRef.current = nextUrls
    setPreviewUrls(nextUrls)
  }

  const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = Array.from(event.target.files ?? [])
    if (selectedFiles.length === 0) return

    const nextFiles = [...files, ...selectedFiles]
    setValue(name, nextFiles as never, {
      shouldDirty: true,
      shouldTouch: true,
      shouldValidate: true,
    })
    replacePreviews(nextFiles)
    event.target.value = ''
  }

  const removeFile = (index: number) => {
    const nextFiles = files.filter((_, fileIndex) => fileIndex !== index)
    setValue(name, nextFiles as never, {
      shouldDirty: true,
      shouldTouch: true,
      shouldValidate: true,
    })
    replacePreviews(nextFiles)
    if (inputRef.current) inputRef.current.value = ''
  }

  const openPicker = () => inputRef.current?.click()

  return (
    <div className="flex w-full flex-col gap-1.5">
      {label && <label className="text-sm font-medium text-gray-800">{label}</label>}

      {files.length > 0 ? (
        <div
          className={[
            'rounded-xl border bg-gray-50 p-2',
            hasError ? 'border-red-400' : 'border-gray-200',
          ].join(' ')}
        >
          <div className="grid grid-cols-2 gap-2 sm:grid-cols-3">
            {files.map((file, index) => (
              <div
                key={`${file.name}-${file.lastModified}-${index}`}
                className="relative aspect-4/3 w-full"
              >
                {previewUrls[index] && (
                  <Image
                    src={previewUrls[index]}
                    alt={`Предпросмотр фото ${index + 1}`}
                    fill
                    unoptimized
                    className="rounded-lg object-cover"
                  />
                )}
                <button
                  type="button"
                  onClick={() => removeFile(index)}
                  className="absolute top-2 right-2 flex size-8 items-center justify-center rounded-lg bg-black/60 text-white backdrop-blur transition-colors hover:bg-black/80"
                  aria-label={`Удалить фото ${index + 1}`}
                >
                  <X className="size-4" />
                </button>
              </div>
            ))}
          </div>
          <button
            type="button"
            onClick={openPicker}
            className="mt-2 flex h-10 w-full items-center justify-center gap-2 rounded-lg border border-dashed border-gray-300 text-sm font-medium text-gray-600 hover:border-orange-400 hover:bg-orange-50/30"
          >
            <ImagePlus className="size-4" />
            Добавить ещё фото
          </button>
        </div>
      ) : (
        <button
          type="button"
          onClick={openPicker}
          className={[
            'flex h-32 w-full flex-col items-center justify-center rounded-xl border border-dashed transition-all',
            hasError
              ? 'border-red-400 bg-red-50/30'
              : 'border-gray-300 bg-gray-50/50 hover:border-orange-400 hover:bg-orange-50/30',
          ].join(' ')}
        >
          <span className="mb-2 flex size-10 items-center justify-center rounded-xl bg-white text-gray-400 shadow-sm">
            <ImagePlus className="size-5" />
          </span>
          <span className="text-sm font-medium text-gray-700">Добавить фотографии</span>
          <span className="mt-1 text-xs text-gray-400">JPG, PNG или WEBP</span>
        </button>
      )}

      <input
        ref={inputRef}
        type="file"
        accept={accept}
        multiple
        onChange={handleChange}
        className="hidden"
      />

      {typeof error === 'string' && (
        <span className="text-xs font-medium text-red-500">{error}</span>
      )}
    </div>
  )
}

export { FormMediaInput }
