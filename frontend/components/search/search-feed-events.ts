/** Событие открытия попапа на карте: лента прокручивается к карточке и подсвечивает её. */
export const SEARCH_FEED_SELECT_EVENT = 'search-map:feed-select'
/** Событие закрытия попапа: подсветка карточки снимается. */
export const SEARCH_FEED_DESELECT_EVENT = 'search-map:feed-deselect'

export function selectFeedItem(itemId: string) {
  window.dispatchEvent(new CustomEvent(SEARCH_FEED_SELECT_EVENT, { detail: { itemId } }))
}

export function deselectFeedItem() {
  window.dispatchEvent(new Event(SEARCH_FEED_DESELECT_EVENT))
}