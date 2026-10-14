'use client'

import React from 'react'
import Image from 'next/image'
import Slider from 'react-slick'
import { Trash2 } from 'lucide-react'
import { ImagesSliderProps } from '@/types'
import { getProxiedImageUrl } from '@/lib/utils/image-proxy'

const ImagesGallery: React.FC<ImagesSliderProps> = ({
  items,
  sliderRef,
  onRemove,
  removingImageId,
}) => {
  const settings = {
    dots: true,
    infinite: true,
    arrows: false,
    speed: 500,
    slidesToShow: 3,
    slidesToScroll: 1,
    responsive: [
      {
        breakpoint: 1280,
        settings: {
          slidesToShow: 2,
          dots: true,
        },
      },
      {
        breakpoint: 768,
        settings: {
          slidesToShow: 1,
          dots: true,
          centerMode: true,
          centerPadding: '40px',
        },
      },
      {
        breakpoint: 480,
        settings: {
          slidesToShow: 1,
          dots: true,
          centerMode: false,
          centerPadding: '0px',
        },
      },
    ],
  }

  return (
    <div className="mx-auto w-full max-w-300">
      <Slider ref={sliderRef} {...settings} className="slick-slider-custom">
        {items.map(item => (
          <div key={item.id} className="px-1 sm:px-2">
            <div className="mx-auto max-w-75 sm:max-w-none">
              <div className="relative aspect-square w-full overflow-hidden rounded-lg sm:aspect-4/5 lg:aspect-316/580">
                <Image
                  src={getProxiedImageUrl(item.image)}
                  alt={`Фото ${item.id}`}
                  fill
                  sizes="(max-width: 480px) 90vw, (max-width: 768px) 45vw, (max-width: 1280px) 30vw, 25vw"
                  priority={item.id <= 4}
                  className="object-cover transition-transform duration-300 hover:scale-105"
                />
                {onRemove && (
                  <button
                    type="button"
                    title="Удалить фотографию"
                    aria-label="Удалить фотографию"
                    disabled={removingImageId === item.id}
                    onClick={() => onRemove(item.id)}
                    className="absolute top-2 right-2 z-10 flex size-9 items-center justify-center rounded-lg bg-black/60 text-white transition-colors hover:bg-red-600 disabled:opacity-50"
                  >
                    <Trash2 className="size-4" />
                  </button>
                )}
              </div>
            </div>
          </div>
        ))}
      </Slider>
    </div>
  )
}

export default ImagesGallery
