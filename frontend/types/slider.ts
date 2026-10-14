export interface MediaItem {
  id: number
  image: string
}

export interface ImagesSliderProps {
  items: MediaItem[]
  onRemove?: (id: number) => void
  removingImageId?: number
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  sliderRef: React.RefObject<any>
}
