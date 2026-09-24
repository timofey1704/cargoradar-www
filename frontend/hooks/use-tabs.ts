import { useCallback, useLayoutEffect, useRef, useState } from 'react'

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

  const refs = useRef(
    Object.fromEntries(tabs.map(tab => [tab, { current: null }])) as {
      [K in T]: React.RefObject<HTMLButtonElement | null>
    }
  ).current

  const updateIndicator = useCallback(() => {
    if (!selectedTab) {
      setIndicatorStyle(prev => ({
        ...prev,
        opacity: 0,
      }))

      return
    }

    const element = refs[selectedTab]?.current

    if (!element) {
      return
    }

    setIndicatorStyle({
      left: element.offsetLeft,
      width: element.offsetWidth,
      opacity: 1,
    })
  }, [refs, selectedTab])

  useLayoutEffect(() => {
    updateIndicator()
  }, [updateIndicator])

  useLayoutEffect(() => {
    if (!selectedTab) {
      return
    }

    const element = refs[selectedTab]?.current

    if (!element) {
      return
    }

    const observer = new ResizeObserver(() => {
      updateIndicator()
    })

    observer.observe(element)

    return () => {
      observer.disconnect()
    }
  }, [refs, selectedTab, updateIndicator])

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
    refs,
  }
}
