import { NextRequest, NextResponse } from 'next/server'

export async function GET(request: NextRequest) {
  const apiUrl =
    process.env.INTERNAL_API_URL ?? process.env.NEXT_PUBLIC_API_URL ?? 'http://127.0.0.1:8000/api'
  const backendOrigin = new URL(apiUrl).origin

  const path = request.nextUrl.pathname.replace(/^\/api\/media\//, '')
  const backendPath = path.startsWith('uploads/') ? path : `media/${path}`
  const imageUrl = new URL(`/${backendPath}`, backendOrigin)

  try {
    const response = await fetch(imageUrl)

    if (!response.ok) {
      console.error('Image not found on backend')
      return new NextResponse('Image not found', { status: 404 })
    }

    return new NextResponse(response.body, {
      headers: {
        'Content-Type': response.headers.get('Content-Type') || 'image/jpeg',
        'Cache-Control': 'public, max-age=31536000, immutable',
      },
    })
  } catch (error) {
    console.error('Error proxying image:', error)
    if (error instanceof Error) {
      console.error('Error message:', error.message)
      console.error('Error stack:', error.stack)
    }
    return new NextResponse('Error loading image', { status: 500 })
  }
}
