import type { ReactNode, KeyboardEvent } from 'react'

export interface TabConfig<T extends string> {
  id: T
  label: ReactNode
  mobileLabel?: ReactNode
  disabled?: boolean
}

interface TabsContainerProps<T extends string> {
  tabs: readonly TabConfig<T>[]
  selectedTab: T | null
  indicatorStyle: {
    left: number
    width: number
    opacity?: number
  }
  tabElements: Record<T, HTMLButtonElement | null>
  registerTab: (tab: T, element: HTMLButtonElement | null) => void
  onTabChange: (tab: T) => void
  rightContent?: ReactNode
}

export function TabsContainer<T extends string>({
  tabs,
  selectedTab,
  indicatorStyle,
  tabElements,
  registerTab,
  onTabChange,
  rightContent,
}: TabsContainerProps<T>) {
  const handleKeyDown = (event: KeyboardEvent<HTMLButtonElement>, currentIndex: number) => {
    let nextIndex: number | null = null

    switch (event.key) {
      case 'ArrowRight':
        nextIndex = (currentIndex + 1) % tabs.length
        break

      case 'ArrowLeft':
        nextIndex = (currentIndex - 1 + tabs.length) % tabs.length
        break

      case 'Home':
        nextIndex = 0
        break

      case 'End':
        nextIndex = tabs.length - 1
        break

      default:
        return
    }

    event.preventDefault()

    const nextTab = tabs[nextIndex]

    if (!nextTab || nextTab.disabled) {
      return
    }

    onTabChange(nextTab.id)
    tabElements[nextTab.id]?.focus()
  }

  return (
    <div className="relative">
      <div className="flex items-center justify-between border-b border-white">
        <div className="grow scrollbar-none overflow-x-auto overflow-y-hidden [-ms-overflow-style:none] [&::-webkit-scrollbar]:hidden">
          <div role="tablist" className="relative flex min-w-min flex-row">
            {tabs.map((tab, index) => {
              const isSelected = selectedTab === tab.id

              return (
                <button
                  key={tab.id}
                  ref={element => registerTab(tab.id, element)}
                  type="button"
                  role="tab"
                  aria-selected={isSelected}
                  aria-disabled={tab.disabled}
                  disabled={tab.disabled}
                  tabIndex={isSelected ? 0 : -1}
                  onClick={() => onTabChange(tab.id)}
                  onKeyDown={event => handleKeyDown(event, index)}
                  className={[
                    'relative shrink-0 px-4 py-2',
                    'whitespace-nowrap',
                    'cursor-pointer',
                    'transition-colors',
                    'focus-visible:outline-none',
                    'focus-visible:ring-2',
                    'focus-visible:ring-blue-700',
                    'focus-visible:ring-offset-2',
                    'disabled:cursor-not-allowed',
                    'disabled:opacity-50',
                    isSelected ? 'text-black' : 'text-black hover:bg-gray-100',
                  ].join(' ')}
                >
                  {tab.mobileLabel ? (
                    <>
                      <span className="block sm:hidden">{tab.mobileLabel}</span>

                      <span className="hidden sm:block">{tab.label}</span>
                    </>
                  ) : (
                    tab.label
                  )}
                </button>
              )
            })}

            <div
              aria-hidden="true"
              className="pointer-events-none absolute -bottom-px h-0.5 bg-blue-700 transition-all duration-200"
              style={{
                left: indicatorStyle.left,
                width: indicatorStyle.width,
                opacity: indicatorStyle.opacity ?? 1,
              }}
            />
          </div>
        </div>

        {rightContent && <div className="ml-4 shrink-0">{rightContent}</div>}
      </div>
    </div>
  )
}
