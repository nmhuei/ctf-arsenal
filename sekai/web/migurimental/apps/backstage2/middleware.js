import { NextResponse } from 'next/server'

export function middleware(request) {
  const remoteAddress =
    request.headers.get('x-real-migu') || ''

  if (remoteAddress !== '1.3.3.7') {
    const url = new URL('/rejected', request.url)
    return NextResponse.redirect(url, 302)
  }

  return NextResponse.next()
}

export const config = {
  matcher: ['/'],
}
