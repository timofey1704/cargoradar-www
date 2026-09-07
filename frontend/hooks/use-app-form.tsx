'use client'

import { useCallback, useState } from 'react'
import { useForm } from 'react-hook-form'
import type {
  DefaultValues,
  FieldValues,
  Resolver,
  SubmitErrorHandler,
  SubmitHandler,
} from 'react-hook-form'

import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'

type AppFormSchema = z.ZodType<FieldValues, FieldValues>

interface UseAppFormOptions<TSchema extends AppFormSchema> {
  schema: TSchema
  defaultValues: DefaultValues<z.input<TSchema>>

  /**
   * Если true — после успешной отправки формы (onValid в handleSubmit отработал
   * без ошибок и его промис зарезолвился) все поля сбрасываются до defaultValues.
   *
   * ВАЖНО: чтобы сброс происходил действительно ПОСЛЕ выполнения запроса,
   * onValid должен возвращать промис, резолвящийся при успехе.
   * Для react-query используйте mutateAsync, а не mutate (mutate резолвится сразу).
   */
  onClean?: boolean
}

export function useAppForm<TSchema extends AppFormSchema>({
  schema,
  defaultValues,
  onClean = false,
}: UseAppFormOptions<TSchema>) {
  const [isVisible, setIsVisible] = useState(false)

  const resolver = zodResolver(schema) as unknown as Resolver<
    z.input<TSchema>,
    unknown,
    z.output<TSchema>
  >

  const form = useForm<z.input<TSchema>, unknown, z.output<TSchema>>({
    defaultValues,
    resolver,
    mode: 'onSubmit',
  })

  const togglePasswordVisibility = useCallback(() => {
    setIsVisible(prev => !prev)
  }, [])

  /**
   * Обёртка над form.handleSubmit: дополнительно сбрасывает поля к defaultValues,
   * если onClean === true и onValid отработал успешно.
   * Возвращается как handleSubmit, чтобы страницы могли вешать его на <form onSubmit>.
   */
  const handleSubmit = useCallback(
    (
      onValid: SubmitHandler<z.output<TSchema>, unknown>,
      onInvalid?: SubmitErrorHandler<z.input<TSchema>>,
    ) =>
      form.handleSubmit<Promise<void>>(
        async (values, event) => {
          await onValid(values, event)

          if (onClean) {
            form.reset(defaultValues)
          }
        },
        onInvalid,
      ),
    [form, onClean, defaultValues],
  )

  return {
    form,
    isVisible,
    togglePasswordVisibility,
    handleSubmit,
  }
}
