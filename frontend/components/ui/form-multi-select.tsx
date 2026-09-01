'use client'

import Select, {
  type GroupBase,
  type OptionsOrGroups,
  type Props as SelectProps,
} from 'react-select'
import { useFormContext } from 'react-hook-form'
import type { FieldValues, Path, PathValue } from 'react-hook-form'

export interface FormMultiSelectOption<TValue extends string = string> {
  value: TValue
  label: string
}

interface FormMultiSelectProps<T extends FieldValues> extends Omit<
  SelectProps<FormMultiSelectOption<string>, true, GroupBase<FormMultiSelectOption<string>>>,
  'name' | 'options' | 'value' | 'onChange'
> {
  name: Path<T>
  label?: string
  options: OptionsOrGroups<FormMultiSelectOption<string>, GroupBase<FormMultiSelectOption<string>>>
  placeholder?: string
}

function FormMultiSelect<T extends FieldValues>({
  name,
  label,
  options,
  placeholder = 'Выберите вариант',
  isDisabled,
  isLoading,
  ...props
}: FormMultiSelectProps<T>) {
  const {
    watch,
    setValue,
    formState: { errors },
  } = useFormContext<T>()

  const rawValue = watch(name)
  const selectedValues = Array.isArray(rawValue)
    ? rawValue.filter((value: unknown): value is string => typeof value === 'string')
    : []
  const flattenOptions = (
    Array.isArray(options)
      ? options
      : options.flatMap(group => ('options' in group ? group.options : [group]))
  ) as FormMultiSelectOption<string>[]

  const selectedOptions = flattenOptions.filter(option => selectedValues.includes(option.value))
  const error = errors[name]?.message
  const hasError = Boolean(error)

  return (
    <div className="flex w-full flex-col gap-1.5">
      {label && (
        <label htmlFor={name} className="text-sm font-medium text-gray-800">
          {label}
        </label>
      )}

      <Select
        {...props}
        inputId={name}
        instanceId={name}
        options={options}
        value={selectedOptions}
        placeholder={placeholder}
        isDisabled={isDisabled}
        isLoading={isLoading}
        isSearchable
        isMulti
        onChange={selected => {
          const nextValue = Array.isArray(selected) ? selected.map(option => option.value) : []
          const normalizedValue =
            nextValue.includes('all') && nextValue.length > 1
              ? nextValue.filter(value => value !== 'all')
              : nextValue

          setValue(name, normalizedValue as PathValue<T, Path<T>>, {
            shouldDirty: true,
            shouldTouch: true,
            shouldValidate: true,
          })
        }}
        filterOption={(option, inputValue) =>
          option.label.toLowerCase().includes(inputValue.trim().toLowerCase())
        }
        noOptionsMessage={({ inputValue }) =>
          inputValue.trim() ? 'Ничего не найдено' : 'Нет доступных вариантов'
        }
        classNames={{
          control: state =>
            [
              '!min-h-13 !rounded-xl !bg-white !border',
              '!px-1 !shadow-none',
              'transition-all duration-200',
              state.isFocused
                ? hasError
                  ? '!border-red-400 !ring-2 !ring-red-400/15'
                  : '!border-orange-500 !ring-2 !ring-orange-500/15'
                : hasError
                  ? '!border-red-400'
                  : '!border-gray-200',
              state.isDisabled ? '!bg-gray-50' : '',
            ].join(' '),

          valueContainer: () => '!px-3 !py-1',

          placeholder: () => '!text-gray-400 !text-sm',

          input: () => '!text-sm !text-gray-900',

          multiValue: () => '!rounded-lg !border !border-orange-100 !bg-orange-50',

          multiValueLabel: () => '!px-2 !py-1 !text-xs !text-orange-700',

          multiValueRemove: () => '!text-orange-600 hover:!bg-orange-100 hover:!text-orange-800',

          menu: () => '!rounded-xl !border !border-gray-200 !overflow-hidden !shadow-xl !mt-1',

          menuList: () => '!p-1',

          option: state =>
            [
              '!rounded-lg !px-3 !py-2.5 !text-sm !cursor-pointer',
              state.isSelected
                ? '!bg-orange-500 !text-white'
                : state.isFocused
                  ? '!bg-orange-50 !text-gray-900'
                  : '!text-gray-900',
            ].join(' '),

          indicatorSeparator: () => '!hidden',

          dropdownIndicator: state =>
            ['!text-gray-400', state.isFocused ? '!text-orange-500' : ''].join(' '),

          clearIndicator: () => '!text-gray-400',

          loadingIndicator: () => '!text-orange-500',
        }}
      />

      {typeof error === 'string' && (
        <span id={`${name}-error`} className="text-xs font-medium text-red-500">
          {error}
        </span>
      )}
    </div>
  )
}

export { FormMultiSelect }
