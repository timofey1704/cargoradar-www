import React from 'react'
import { getFeed } from '@/lib/search/get-feed'

const SearchPage = async () => {
  const feed = await getFeed()
  console.log(feed)
  return <div>SearchPage</div>
}

export default SearchPage
