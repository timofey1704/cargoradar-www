'use client'

import { useEffect } from 'react'

import { SEARCH_FEED_DESELECT_EVENT, SEARCH_FEED_SELECT_EVENT } from './search-feed-events'

const HIGHLIGHT_CLASSES = ['ring-2', 'ring-orange']

/**
 * Слушает события попапов карты: прокручивает ленту к карточке
 * и подсвечивает её, пока попап открыт.
 */
export function SearchFeedHighlight() {
  useEffect(() => {
    let active: HTMLElement | null = null

    const clear = () => {
      if (!active) return
      active.classList.remove(...HIGHLIGHT_CLASSES)
      active = null
    }

    const onSelect = (event: Event) => {
      const itemId = (event as CustomEvent<{ itemId: string }>).detail?.itemId
      if (!itemId) return

      clear()

      const card = document.getElementById(`feed-item-${itemId}`)
      if (!card) return

      card.classList.add(...HIGHLIGHT_CLASSES)
      active = card
      card.scrollIntoView({ behavior: 'smooth', block: 'center' })
    }

    const onDeselect = () => clear()

    window.addEventListener(SEARCH_FEED_SELECT_EVENT, onSelect)
    window.addEventListener(SEARCH_FEED_DESELECT_EVENT, onDeselect)

    return () => {
      window.removeEventListener(SEARCH_FEED_SELECT_EVENT, onSelect)
      window.removeEventListener(SEARCH_FEED_DESELECT_EVENT, onDeselect)
      clear()
    }
  }, [])

  return null
}