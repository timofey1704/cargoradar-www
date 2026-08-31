'use client'

import type { InputHTMLAttributes } from 'react'
import {
  useFormContext,
  type FieldValues,
  type Path,
} from 'react-hook-form'

import { EyeOff, Eye } from 'lucide-react'

interface FormInputProps<T extends FieldValues>
  extends Omit<InputHTMLAttributes<HTMLInputElement>, 'name'> {
  name: Path<T>
  label?: string
  isPassword?: boolean
  isVisible?: boolean
  togglePasswordVisibility?: () => void
}

function FormInput<T extends FieldValues>({
  name,
  label,
  isPassword = false,
  isVisible = false,
  togglePasswordVisibility,
  className = '',
  ...props
}: FormInputProps<T>) {
  const {
    register,
    formState: { errors },
  } = useFormContext<T>()

  const error = errors[name]?.message
  const hasError = Boolean(error)

  return (
    <div className="flex w-full flex-col gap-1.5">
      {label && (
        <label
          htmlFor={name}
          className="text-sm font-medium text-gray-800"
        >
          {label}
        </label>
      )}

      <div className="relative">
        <input
          {...props}
          id={name}
          type={
            isPassword && !isVisible
              ? 'password'
              : props.type ?? 'text'
          }
          aria-invalid={hasError}
          aria-describedby={hasError ? `${name}-error` : undefined}
          className={[
            'h-13 w-full rounded-xl border bg-white px-4 text-sm text-gray-900',
            'outline-none transition-all duration-200',
            'placeholder:text-gray-400',
            'focus:ring-2',
            hasError
              ? 'border-red-400 focus:border-red-400 focus:ring-red-400/15'
              : 'border-gray-200 focus:border-orange-500 focus:ring-orange-500/15',
            isPassword ? 'pr-12' : '',
            className,
          ].join(' ')}
          {...register(name)}
        />

        {isPassword && (
          <button
            type="button"
            onClick={togglePasswordVisibility}
            aria-label={
              isVisible
                ? 'Скрыть пароль'
                : 'Показать пароль'
            }
            className="absolute top-1/2 right-3 flex size-9 -translate-y-1/2 items-center justify-center rounded-lg text-gray-400 transition-colors hover:bg-gray-100 hover:text-gray-700"
          >
            {isVisible ? (
              <EyeOff className="size-4" />
            ) : (
              <Eye className="size-4" />
            )}
          </button>
        )}
      </div>

      {typeof error === 'string' && (
        <span
          id={`${name}-error`}
          className="text-xs font-medium text-red-500"
        >
          {error}
        </span>
      )}
    </div>
  )
}

export { FormInput }