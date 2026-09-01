'use client'

import { useFormContext } from 'react-hook-form'
import type { FieldValues, Path } from 'react-hook-form'
import { ImagePlus, X } from 'lucide-react'
import { useEffect, useRef } from 'react'

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

  const {
    watch,
    setValue,
    formState: { errors },
  } = useFormContext<T>()

  const file = watch(name) as File | undefined
  const error = errors[name]?.message
  const hasError = Boolean(error)

  const previewUrl = file ? URL.createObjectURL(file) : null

  useEffect(() => {
    return () => {
      if (previewUrl) {
        URL.revokeObjectURL(previewUrl)
      }
    }
  }, [previewUrl])

  const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0]

    if (!selectedFile) return

    setValue(name, selectedFile as never, {
      shouldDirty: true,
      shouldTouch: true,
      shouldValidate: true,
    })
  }

  const removeFile = () => {
    setValue(name, undefined as never, {
      shouldDirty: true,
      shouldTouch: true,
      shouldValidate: true,
    })

    if (inputRef.current) {
      inputRef.current.value = ''
    }
  }

  return (
    <div className="flex w-full flex-col gap-1.5">
      {label && <label className="text-sm font-medium text-gray-800">{label}</label>}

      {file && previewUrl ? (
        <div
          className={[
            'relative overflow-hidden rounded-xl border bg-gray-50',
            hasError ? 'border-red-400' : 'border-gray-200',
          ].join(' ')}
        >
          <img
            src={previewUrl}
            alt="Предпросмотр автомобиля"
            className="h-48 w-full object-cover"
          />

          <button
            type="button"
            onClick={removeFile}
            className="absolute top-3 right-3 flex size-8 items-center justify-center rounded-lg bg-black/60 text-white backdrop-blur transition-colors hover:bg-black/80"
            aria-label="Удалить фотографию"
          >
            <X className="size-4" />
          </button>
        </div>
      ) : (
        <button
          type="button"
          onClick={() => inputRef.current?.click()}
          className={[
            'flex h-32 w-full flex-col items-center justify-center rounded-xl border border-dashed transition-all',
            hasError
              ? 'border-red-400 bg-red-50/30'
              : 'border-gray-300 bg-gray-50/50 hover:border-orange-400 hover:bg-orange-50/30',
          ].join(' ')}
        >
          <div className="mb-2 flex size-10 items-center justify-center rounded-xl bg-white text-gray-400 shadow-sm">
            <ImagePlus className="size-5" />
          </div>

          <span className="text-sm font-medium text-gray-700">Добавить фотографию</span>

          <span className="mt-1 text-xs text-gray-400">JPG, PNG или WEBP</span>
        </button>
      )}

      <input
        ref={inputRef}
        type="file"
        accept={accept}
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
