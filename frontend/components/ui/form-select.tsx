'use client'

import Select, {
  type GroupBase,
  type OptionsOrGroups,
  type Props as SelectProps,
} from 'react-select'
import { useFormContext } from 'react-hook-form'
import type { FieldValues, Path, PathValue } from 'react-hook-form'

export interface FormSelectOption<TValue extends string | number = string> {
  value: TValue
  label: string
}

interface FormSelectProps<T extends FieldValues> extends Omit<
  SelectProps<FormSelectOption, false, GroupBase<FormSelectOption>>,
  'name' | 'options' | 'value' | 'onChange'
> {
  name: Path<T>
  label?: string
  options: OptionsOrGroups<FormSelectOption, GroupBase<FormSelectOption>>
  placeholder?: string
}

function FormSelect<T extends FieldValues>({
  name,
  label,
  options,
  placeholder = 'Выберите вариант',
  isDisabled,
  isLoading,
  ...props
}: FormSelectProps<T>) {
  const {
    watch,
    setValue,
    formState: { errors },
  } = useFormContext<T>()

  const value = watch(name)
  const error = errors[name]?.message
  const hasError = Boolean(error)

  const selectedOption =
    options
      .flatMap(option => ('options' in option ? option.options : [option]))
      .find(option => option.value === value) ?? null

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
        options={options}
        value={selectedOption}
        placeholder={placeholder}
        isDisabled={isDisabled}
        isLoading={isLoading}
        isSearchable
        onChange={option => {
          setValue(name, (option?.value ?? '') as PathValue<T, Path<T>>, {
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

          valueContainer: () => '!px-3',

          placeholder: () => '!text-gray-400 !text-sm',

          singleValue: () => '!text-sm !text-gray-900',

          input: () => '!text-sm !text-gray-900',

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

export { FormSelect }
