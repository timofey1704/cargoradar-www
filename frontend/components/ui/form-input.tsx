'use client'

import {
  forwardRef,
  type InputHTMLAttributes,
} from 'react'
import {
  useFormContext,
  type FieldValues,
  type Path,
} from 'react-hook-form'

interface FormInputProps<T extends FieldValues>
  extends Omit<InputHTMLAttributes<HTMLInputElement>, 'name'> {
  name: Path<T>
  label?: string
  isPassword?: boolean
  isVisible?: boolean
  togglePasswordVisibility?: () => void
}

const FormInput = forwardRef(
  <T extends FieldValues>(
    {
      name,
      label,
      isPassword = false,
      isVisible = false,
      togglePasswordVisibility,
      ...props
    }: FormInputProps<T>,
    ref: React.ForwardedRef<HTMLInputElement>,
  ) => {
    const {
      register,
      formState: { errors },
    } = useFormContext<T>()

    const error = errors[name]?.message

    return (
      <div className="flex w-full flex-col gap-1">
        {label && (
          <label
            htmlFor={name}
            className="text-sm font-medium"
          >
            {label}
          </label>
        )}

        <div className="relative">
          <input
            {...register(name)}
            {...props}
            ref={ref}
            id={name}
            type={
              isPassword && !isVisible
                ? 'password'
                : props.type ?? 'text'
            }
            className="w-full rounded-xl border px-4 py-3"
          />

          {isPassword && (
            <button
              type="button"
              onClick={togglePasswordVisibility}
              className="absolute top-1/2 right-3 -translate-y-1/2"
            >
              {isVisible ? 'Скрыть' : 'Показать'}
            </button>
          )}
        </div>

        {error && typeof error === 'string' && (
          <span className="text-sm text-red-500">
            {error}
          </span>
        )}
      </div>
    )
  },
)

FormInput.displayName = 'FormInput'

export { FormInput }