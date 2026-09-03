import React from 'react'
import { ArrowRight } from 'lucide-react'
import clsx from 'clsx'

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  isSubmitting?: boolean
  loadingText?: string
  defaultText?: string
  showArrow?: boolean
  icon?: React.ReactNode
  variant?: 'orange' | 'blue' | 'green' | 'red' | 'purple'
  size?: 'sm' | 'md' | 'lg'
  fullWidth?: boolean
}

const variantConfig = {
  orange: {
    bg: 'bg-orange-500 hover:bg-orange-600',
    shadow: 'shadow-orange-500/20 hover:shadow-orange-500/30',
    focus: 'focus:ring-orange-500/30',
  },
  blue: {
    bg: 'bg-blue-500 hover:bg-blue-600',
    shadow: 'shadow-blue-500/20 hover:shadow-blue-500/30',
    focus: 'focus:ring-blue-500/30',
  },
  green: {
    bg: 'bg-green-500 hover:bg-green-600',
    shadow: 'shadow-green-500/20 hover:shadow-green-500/30',
    focus: 'focus:ring-green-500/30',
  },
  red: {
    bg: 'bg-red-500 hover:bg-red-600',
    shadow: 'shadow-red-500/20 hover:shadow-red-500/30',
    focus: 'focus:ring-red-500/30',
  },
  purple: {
    bg: 'bg-purple-500 hover:bg-purple-600',
    shadow: 'shadow-purple-500/20 hover:shadow-purple-500/30',
    focus: 'focus:ring-purple-500/30',
  },
}

const sizeConfig = {
  sm: 'h-9 px-3 text-xs',
  md: 'h-11 px-4 text-sm',
  lg: 'h-13 px-5 text-sm',
}

export const Button: React.FC<ButtonProps> = ({
  isSubmitting = false,
  loadingText = 'Создаём аккаунт...',
  defaultText = 'Зарегистрироваться',
  showArrow = true,
  icon,
  variant = 'orange',
  size = 'lg',
  fullWidth = true,
  className = '',
  disabled,
  children,
  ...props
}) => {
  const styles = variantConfig[variant]
  const isDisabled = disabled || isSubmitting

  return (
    <button
      type="submit"
      disabled={isDisabled}
      className={clsx(
        'flex items-center justify-center gap-2 rounded-xl font-semibold text-white',
        'transition-all duration-200 focus:outline-none',
        styles.bg,
        styles.focus,
        sizeConfig[size],
        {
          'w-full': fullWidth,
          'w-auto': !fullWidth,
          'cursor-not-allowed opacity-60': isDisabled,
        },
        'shadow-lg',
        styles.shadow,
        className
      )}
      {...props}
    >
      {isSubmitting ? (
        <>
          {/* {icon || <span className="animate-spin">⏳</span>} */}
          {children || loadingText}
        </>
      ) : (
        <>
          {children || defaultText}
          {showArrow && <ArrowRight className="size-4" />}
        </>
      )}
    </button>
  )
}
