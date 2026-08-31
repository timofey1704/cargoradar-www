// hooks/use-app-form.tsx
'use client'

import { useCallback, useState } from 'react'
import { useForm } from 'react-hook-form'
import type {
  DefaultValues,
  FieldValues,
  Resolver,
} from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'

type AppFormSchema = z.ZodType<FieldValues, FieldValues>

interface UseAppFormOptions<TSchema extends AppFormSchema> {
  schema: TSchema
  defaultValues: DefaultValues<z.input<TSchema>>
}

export function useAppForm<TSchema extends AppFormSchema>({
  schema,
  defaultValues,
}: UseAppFormOptions<TSchema>) {
  const [isVisible, setIsVisible] = useState(false)

  const resolver = zodResolver(schema) as unknown as Resolver<
    z.input<TSchema>,
    unknown,
    z.output<TSchema>
  >

  const form = useForm<
    z.input<TSchema>,
    unknown,
    z.output<TSchema>
  >({
    defaultValues,
    resolver,
    mode: 'onSubmit',
  })

  const togglePasswordVisibility = useCallback(() => {
    setIsVisible((prev) => !prev)
  }, [])

  return {
    form,
    isVisible,
    togglePasswordVisibility,
  }
}