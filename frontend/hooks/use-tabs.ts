import { useCallback, useLayoutEffect, useState } from 'react'

export interface TabIndicatorStyle {
  left: number
  width: number
  opacity: number
}

export interface UseTabsOptions<T extends string> {
  defaultTab?: T | null
  onTabChange?: (tab: T) => void
}

export function useTabs<T extends string>(tabs: readonly T[], options: UseTabsOptions<T> = {}) {
  const { defaultTab = tabs[0] ?? null, onTabChange } = options

  const [selectedTab, setSelectedTab] = useState<T | null>(defaultTab)

  const [indicatorStyle, setIndicatorStyle] = useState<TabIndicatorStyle>({
    left: 0,
    width: 0,
    opacity: 0,
  })

  const [tabElements, setTabElements] = useState<Record<T, HTMLButtonElement | null>>(
    () => Object.fromEntries(tabs.map(tab => [tab, null])) as Record<T, HTMLButtonElement | null>
  )

  const updateIndicator = useCallback((element: HTMLButtonElement | null) => {
    if (!element) {
      return
    }

    setIndicatorStyle({
      left: element.offsetLeft,
      width: element.offsetWidth,
      opacity: 1,
    })
  }, [])

  const registerTab = useCallback(
    (tab: T, element: HTMLButtonElement | null) => {
      setTabElements(current =>
        current[tab] === element ? current : { ...current, [tab]: element }
      )

      if (selectedTab === tab) {
        updateIndicator(element)
      }
    },
    [selectedTab, updateIndicator]
  )

  useLayoutEffect(() => {
    if (!selectedTab) {
      return
    }

    const element = tabElements[selectedTab]

    if (!element) {
      return
    }

    const observer = new ResizeObserver(() => {
      updateIndicator(element)
    })

    observer.observe(element)

    return () => {
      observer.disconnect()
    }
  }, [tabElements, selectedTab, updateIndicator])

  const setTab = useCallback(
    (tab: T) => {
      if (tab === selectedTab) {
        return
      }

      setSelectedTab(tab)
      onTabChange?.(tab)
    },
    [onTabChange, selectedTab]
  )

  return {
    selectedTab,
    setTab,
    indicatorStyle,
    tabElements,
    registerTab,
  }
}
